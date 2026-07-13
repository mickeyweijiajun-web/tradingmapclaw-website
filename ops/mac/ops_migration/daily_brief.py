#!/usr/bin/env python3
"""TMC daily market brief — migrated from Perplexity cron 9b9748d6.

Owner: LOCAL-DUAL-ENGINE (Hermes generates, independent numeric verifier checks)
Schedule: launchd ai.tmc.daily_brief, Mon-Fri 08:00 Asia/Shanghai (09:00 JST)

Pipeline:
  1. Fetch quotes from TWO independent sources per asset, cross-check (±1.5%).
     Disagreement or failure -> DATA_UNAVAILABLE (never guess).
  2. Hermes (`hermes -z`) writes commentary from verified numbers ONLY.
  3. Independent verification pass: re-extract every number in the draft and
     check against source data; scan for forbidden language and future dates.
  4. Send to Telegram via `hermes send -t telegram` (skipped on --dry-run or
     verification failure).

Red lines: as-of timestamps everywhere; scenario labels only (no buy/sell);
no future dates; DATA_UNAVAILABLE over guessing. Does NOT touch memory.sqlite,
stocks.yaml, orders, or any internal scheduler state.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

HOME = Path.home()
OPS = HOME / "TradingMapClaw" / "ops_migration"
LOGDIR = OPS / "logs"
HERMES = str(HOME / ".local" / "bin" / "hermes")

# Ticker mapping: canonical -> per-source symbol
EQUITIES = ["MSFT", "META", "NVDA", "CRWV", "RKLB", "AVGO", "NOW", "SPCX"]
CRYPTO = ["BTC", "ETH"]
STOOQ = {t: f"{t.lower()}.us" for t in EQUITIES}
TOLERANCE = 0.015  # 1.5%

FORBIDDEN = [r"\bbuy now\b", r"\byou should (buy|sell)\b", r"\bguaranteed\b",
             r"\bcan'?t lose\b", r"\bbeat the market\b", r"稳赚", r"保证收益"]


def http_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "tmc-brief/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def http_text(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "tmc-brief/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


def fetch_equity(tk):
    """Two sources: Stooq CSV + Yahoo chart API. Return dict or DATA_UNAVAILABLE."""
    prices = {}
    try:  # source 1: stooq daily close
        csv = http_text(f"https://stooq.com/q/l/?s={STOOQ[tk]}&f=sd2t2ohlcv&h&e=csv")
        row = csv.strip().splitlines()[1].split(",")
        prices["stooq"] = {"close": float(row[6]), "date": row[1]}
    except Exception as e:
        prices["stooq"] = {"error": str(e)[:80]}
    try:  # source 2: yahoo
        d = http_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?range=5d&interval=1d")
        res = d["chart"]["result"][0]
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c]
        ts = res["timestamp"][-1]
        prices["yahoo"] = {"close": round(closes[-1], 2),
                           "prev": round(closes[-2], 2) if len(closes) > 1 else None,
                           "date": dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).date().isoformat()}
    except Exception as e:
        prices["yahoo"] = {"error": str(e)[:80]}
    ok = [s for s in ("stooq", "yahoo") if "close" in prices[s]]
    if len(ok) < 2:
        return {"ticker": tk, "status": "DATA_UNAVAILABLE", "detail": prices}
    a, b = prices["stooq"]["close"], prices["yahoo"]["close"]
    if abs(a - b) / max(a, b) > TOLERANCE:
        return {"ticker": tk, "status": "DATA_UNAVAILABLE",
                "detail": f"cross-check failed stooq={a} yahoo={b}"}
    chg = None
    if prices["yahoo"].get("prev"):
        chg = round((b - prices["yahoo"]["prev"]) / prices["yahoo"]["prev"] * 100, 2)
    return {"ticker": tk, "status": "OK", "close": b, "change_pct": chg,
            "as_of": prices["yahoo"]["date"], "sources": ["stooq", "yahoo"]}


def fetch_crypto(sym):
    prices = {}
    try:
        d = http_json(f"https://api.coinbase.com/v2/prices/{sym}-USD/spot")
        prices["coinbase"] = float(d["data"]["amount"])
    except Exception as e:
        prices["coinbase"] = None
    try:
        d = http_json(f"https://api.binance.com/api/v3/ticker/price?symbol={sym}USDT")
        prices["binance"] = float(d["price"])
    except Exception:
        prices["binance"] = None
    vals = [v for v in prices.values() if v]
    if len(vals) < 2 or abs(vals[0] - vals[1]) / max(vals) > TOLERANCE:
        return {"ticker": sym, "status": "DATA_UNAVAILABLE", "detail": prices}
    now = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return {"ticker": sym, "status": "OK", "close": round(sum(vals) / 2, 2),
            "as_of": now, "sources": ["coinbase", "binance"]}


def hermes_generate(data, today):
    facts = json.dumps(data, ensure_ascii=False, indent=1)
    prompt = f"""You write TradingMapClaw's daily market brief (English, Telegram, <=600 words).
Today is {today}. Use ONLY the verified data below — every number you mention must come from it verbatim.
Rules: cite as-of dates; tickers with DATA_UNAVAILABLE must be listed as DATA_UNAVAILABLE (never guess);
scenario language only (bullish/neutral/bearish) — NO buy/sell/hold advice; no future dates; no guarantees;
end with: "Research & education only. Not investment advice."
Format: title line with date; B-group equities section; crypto section; one 'what to watch' paragraph.
DATA:
{facts}"""
    cp = subprocess.run([HERMES, "-z", prompt], capture_output=True, text=True, timeout=600)
    return cp.stdout.strip() if cp.returncode == 0 else None


def verify(draft, data, today):
    """Independent check: numbers, forbidden language, future dates."""
    problems = []
    ok_map = {d["ticker"]: d for d in data if d["status"] == "OK"}
    for m in re.finditer(r"\b([A-Z]{2,5})\b[^.\n]{0,40}?\$?(\d{2,6}(?:,\d{3})?\.?\d{0,2})", draft):
        tk, num = m.group(1), float(m.group(2).replace(",", ""))
        if tk in ok_map and num > 10:
            ref = ok_map[tk]["close"]
            if abs(num - ref) / ref > 0.02 and abs(num) not in (abs(ok_map[tk].get("change_pct") or 0),):
                problems.append(f"number mismatch {tk}: draft={num} verified={ref}")
    for pat in FORBIDDEN:
        if re.search(pat, draft, re.I):
            problems.append(f"forbidden language: {pat}")
    for m in re.finditer(r"\b(20\d\d-\d\d-\d\d)\b", draft):
        if m.group(1) > today:
            problems.append(f"future date: {m.group(1)}")
    for d in data:
        if d["status"] == "DATA_UNAVAILABLE" and d["ticker"] not in draft:
            problems.append(f"{d['ticker']} unavailable but not disclosed in draft")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-llm", action="store_true", help="data-only run (no hermes)")
    args = ap.parse_args()
    tz = ZoneInfo("Asia/Shanghai")
    today = dt.datetime.now(tz).date().isoformat()
    LOGDIR.mkdir(parents=True, exist_ok=True)
    log = {"run_at": dt.datetime.now(tz).isoformat(), "dry_run": args.dry_run, "owner": "LOCAL-DUAL-ENGINE"}

    data = [fetch_equity(t) for t in EQUITIES] + [fetch_crypto(c) for c in CRYPTO]
    log["data"] = data
    unavailable = [d["ticker"] for d in data if d["status"] != "OK"]

    if args.skip_llm:
        draft = None
        log["mode"] = "data-only"
    else:
        draft = hermes_generate(data, today)
        log["hermes_ok"] = bool(draft)
    sent = False
    if draft:
        problems = verify(draft, data, today)
        log["verify_problems"] = problems
        (LOGDIR / f"brief-{today}.md").write_text(draft)
        if problems:
            print("VERIFICATION FAILED — not sending:\n" + "\n".join(problems))
        elif args.dry_run:
            print("[dry-run] verified draft ready, not sending")
        else:
            cp = subprocess.run([HERMES, "send", "-t", "telegram"], input=draft,
                                capture_output=True, text=True, timeout=120)
            sent = cp.returncode == 0
            log["telegram_rc"] = cp.returncode
    log["sent"] = sent
    log["data_unavailable"] = unavailable
    (LOGDIR / f"daily_brief-{today}.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))
    print(f"OK={len(data)-len(unavailable)}/{len(data)} unavailable={unavailable} sent={sent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
