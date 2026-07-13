#!/usr/bin/env python3
"""weekly_brief_mvp.py — TMC Weekly Market Intelligence Brief (MVP pipeline).

End-to-end data step: fetch dual-source verified prices for the MVP watchlist
(B-group equities + BTC/ETH), compute 5-trading-day change, and write
site/data/radar-latest.json (+ a period archive copy site/data/radar-<PERIOD>.json).

Data red lines (docs/MIGRATION_MATRIX.md):
  - Dual source: equities Yahoo + Nasdaq (Stooq/Binance are blocked from this runner:
    Stooq serves a JS proof-of-work wall, Binance returns HTTP 451; substitutes are
    independent primary sources); crypto Coinbase + Kraken.
  - Tolerance 1.5% between sources; disagreement -> DATA_UNAVAILABLE, never guess.
  - No fabricated metrics: no S-Factor here (that is the local engine's metric).
    verified_by states exactly what THIS pipeline verified.

Usage: python3 tools/weekly_brief_mvp.py [--out-dir site/data]
Exit codes: 0 ok (some rows may be DATA_UNAVAILABLE), 1 fatal (no rows).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EQUITIES = [
    ("MSFT", "Software · Cloud"),
    ("META", "Social · Advertising"),
    ("NVDA", "Semiconductors · AI"),
    ("CRWV", "AI Cloud Infrastructure"),
    ("RKLB", "Space · Launch"),
    ("AVGO", "Semiconductors · Networking"),
    ("NOW", "Enterprise Software"),
]
CRYPTO = [("BTC", "Crypto · L1"), ("ETH", "Crypto · L1")]
TOLERANCE = 0.015  # 1.5%
UA = {"User-Agent": "Mozilla/5.0 (TMC research pipeline; contact tradingmapclaw.com)"}


def _get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def nasdaq_closes(sym: str):
    """Return list of (iso_date, close) ascending from Nasdaq chart API."""
    today = dt.date.today()
    frm = today - dt.timedelta(days=35)
    js = json.loads(_get(
        f"https://api.nasdaq.com/api/quote/{sym}/chart?assetclass=stocks"
        f"&fromdate={frm.isoformat()}&todate={today.isoformat()}"))
    out = []
    for p in (js.get("data") or {}).get("chart") or []:
        z = p.get("z") or {}
        d, c = z.get("dateTime"), z.get("close")
        if d and c:
            m, dd, y = d.split("/")
            out.append((f"{y}-{int(m):02d}-{int(dd):02d}", float(c.replace(",", ""))))
    return sorted(out)


def yahoo_closes(sym: str):
    js = json.loads(_get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1mo&interval=1d"))
    res = js["chart"]["result"][0]
    ts = res["timestamp"]
    closes = res["indicators"]["quote"][0]["close"]
    out = []
    for t, c in zip(ts, closes):
        if c is not None:
            out.append((dt.datetime.utcfromtimestamp(t).date().isoformat(), round(float(c), 4)))
    return out


def five_day_change(closes, as_of: str):
    """pct change: close(as_of) vs close 5 trading days earlier."""
    dates = [d for d, _ in closes]
    if as_of not in dates:
        return None, None
    i = dates.index(as_of)
    if i < 5:
        return None, None
    last, prev = closes[i][1], closes[i - 5][1]
    return (last / prev - 1.0) * 100.0, last


def crypto_pair(sym: str):
    """(coinbase_5d_pct, kraken_5d_pct, spots) using daily candles, as of latest UTC day."""
    # Coinbase Exchange daily candles: [time, low, high, open, close, volume], newest first
    cb = json.loads(_get(
        f"https://api.exchange.coinbase.com/products/{sym}-USD/candles?granularity=86400"))
    cb_sorted = sorted(cb, key=lambda r: r[0])
    cb_closes = [(dt.datetime.fromtimestamp(r[0], dt.timezone.utc).date().isoformat(), float(r[4]))
                 for r in cb_sorted]
    kr_pair = "XBTUSD" if sym == "BTC" else f"{sym}USD"
    kr = json.loads(_get(
        f"https://api.kraken.com/0/public/OHLC?pair={kr_pair}&interval=1440"))
    kr_rows = list(kr["result"].values())[0]
    bn_closes = [(dt.datetime.fromtimestamp(r[0], dt.timezone.utc).date().isoformat(), float(r[4]))
                 for r in kr_rows]
    def chg(closes):
        if len(closes) < 6:
            return None, None
        return (closes[-1][1] / closes[-6][1] - 1.0) * 100.0, closes[-1][1]
    (c_pct, c_last), (b_pct, b_last) = chg(cb_closes), chg(bn_closes)
    return c_pct, b_pct, c_last, b_last, cb_closes[-1][0] if cb_closes else None


def band_for(pct: float) -> str:
    a = abs(pct)
    if a >= 8.0:
        return "high-research-priority"
    if a >= 3.0:
        return "watch"
    return "logged"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(REPO_ROOT / "site" / "data"))
    args = ap.parse_args()
    out_dir = Path(args.out_dir)

    today = dt.date.today()
    period = f"{today.isocalendar()[0]}-W{today.isocalendar()[1]:02d}"

    rows, problems = [], []
    eq_as_of = None
    for sym, sector in EQUITIES:
        try:
            st, ya = nasdaq_closes(sym), yahoo_closes(sym)
        except Exception as e:
            problems.append(f"{sym}: fetch error {e}")
            rows.append({"ticker": sym, "sector": sector, "status": "DATA_UNAVAILABLE",
                         "reason": "source fetch error"})
            continue
        as_of = min(st[-1][0], ya[-1][0])  # last date both sources have
        eq_as_of = max(eq_as_of or as_of, as_of) if eq_as_of else as_of
        s_pct, s_last = five_day_change(st, as_of)
        y_pct, y_last = five_day_change(ya, as_of)
        if s_pct is None or y_pct is None:
            rows.append({"ticker": sym, "sector": sector, "status": "DATA_UNAVAILABLE",
                         "reason": f"insufficient history at {as_of}"})
            continue
        if abs(s_last - y_last) / y_last > TOLERANCE:
            rows.append({"ticker": sym, "sector": sector, "status": "DATA_UNAVAILABLE",
                         "reason": f"source disagreement >1.5% (stooq {s_last} vs yahoo {y_last})"})
            continue
        pct = round((s_pct + y_pct) / 2.0, 1)
        rows.append({
            "ticker": sym, "sector": sector, "surge_5d_pct": pct,
            "close": round(y_last, 2), "data_as_of": as_of,
            "band": band_for(pct),
            "verified_by": "dual-source ✓ (Yahoo + Nasdaq, ≤1.5% divergence)",
        })

    for sym, sector in CRYPTO:
        try:
            c_pct, b_pct, c_last, b_last, as_of = crypto_pair(sym)
        except Exception as e:
            problems.append(f"{sym}: fetch error {e}")
            rows.append({"ticker": sym, "sector": sector, "status": "DATA_UNAVAILABLE",
                         "reason": "source fetch error"})
            continue
        if c_pct is None or b_pct is None:
            rows.append({"ticker": sym, "sector": sector, "status": "DATA_UNAVAILABLE",
                         "reason": "insufficient candle history"})
            continue
        if abs(c_last - b_last) / b_last > TOLERANCE:
            rows.append({"ticker": sym, "sector": sector, "status": "DATA_UNAVAILABLE",
                         "reason": f"source disagreement >1.5% (coinbase {c_last} vs kraken {b_last})"})
            continue
        pct = round((c_pct + b_pct) / 2.0, 1)
        rows.append({
            "ticker": sym, "sector": sector, "surge_5d_pct": pct,
            "close": round((c_last + b_last) / 2.0, 2), "data_as_of": as_of,
            "band": band_for(pct),
            "verified_by": "dual-source ✓ (Coinbase + Kraken, ≤1.5% divergence)",
        })

    ok_rows = [r for r in rows if "surge_5d_pct" in r]
    if not ok_rows:
        print("FATAL: no verified rows", problems, file=sys.stderr)
        return 1

    payload = {
        "period": period,
        "data_as_of": eq_as_of or today.isoformat(),
        "published_at": today.isoformat(),
        "is_sample": False,
        "status": "LIVE",
        "next_publication": "auto",
        "scope_note": ("MVP live publication: B-group watchlist subset (7 US equities + BTC/ETH). "
                       "5-trading-day change, dual-source verified. S-Factor engine metrics are "
                       "produced by the local dual-engine system and are not included in this MVP run."),
        "methodology": "close-over-close 5 trading days; two independent sources per asset (equities Yahoo+Nasdaq, crypto Coinbase+Kraken); 1.5% tolerance; disagreement -> DATA_UNAVAILABLE",
        "rows": rows,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "radar-latest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    (out_dir / f"radar-{period}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    print(json.dumps({"period": period, "rows_ok": len(ok_rows),
                      "rows_unavailable": len(rows) - len(ok_rows),
                      "problems": problems}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
