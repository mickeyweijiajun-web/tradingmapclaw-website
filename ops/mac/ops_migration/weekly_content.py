#!/usr/bin/env python3
"""TMC weekly content draft — migrated from Perplexity cron d87c574c.

Owner: LOCAL-DUAL-ENGINE. Schedule: launchd ai.tmc.weekly_content, Mon 09:30 Asia/Shanghai.

Rotates topics by ISO week, reads numbers ONLY from FACTS.md, generates a
Substack-style DRAFT via `hermes -z`, lints it against FACTS red lines, and
saves to ~/TradingMapClaw/public-content/drafts/DRAFT_<date>_<topic>.md.
NEVER publishes anywhere. Sends a Telegram reminder that a draft is ready.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HOME = Path.home()
OPS = HOME / "TradingMapClaw" / "ops_migration"
DRAFTS = HOME / "TradingMapClaw" / "public-content" / "drafts"
LOGDIR = OPS / "logs"
FACTS = OPS / "FACTS.md"
HERMES = str(HOME / ".local" / "bin" / "hermes")

TOPICS = [
    ("dual-engine-verification", "How dual-engine cross-verification catches a confidently wrong model"),
    ("budget-engineering", "Running 100+ scheduled research workflows on a $55/month budget cap"),
    ("engine-disagreement", "What happens when Engine 1 and Engine 2 disagree by more than 5%"),
    ("council-voting", "A 3-round model council vote, explained with a real workflow"),
    ("build-log", "Build log: one operator, one Mac mini, hundreds of scripts"),
    ("method-note", "Method note: why every public number carries an as-of date"),
]

FORBIDDEN = [r"\bbuy now\b", r"\bguaranteed\b", r"\bcan'?t lose\b", r"\bbeat the market\b",
             r"\byou should (buy|sell)\b", r"\bhigh conviction\b", r"\$149\b", r"\$99\b",
             r"three-engine", r"三引擎", r"GPT-5\.5", r"\b119 (scheduled )?jobs\b", r"\b500\+? scripts\b"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--topic", help="override topic slug")
    args = ap.parse_args()
    tz = ZoneInfo("Asia/Shanghai")
    now = dt.datetime.now(tz)
    week = now.isocalendar()[1]
    slug, title = TOPICS[week % len(TOPICS)]
    if args.topic:
        for s, t in TOPICS:
            if s == args.topic:
                slug, title = s, t
    facts = FACTS.read_text() if FACTS.exists() else ""
    if not facts:
        print("FATAL: FACTS.md missing — refusing to generate without the canon")
        return 1
    prompt = f"""Write a Substack draft (900-1300 words, English) for TradingMapClaw.
Topic: {title}
Voice: first-person solo builder ("the one-handed operator"), concrete, no hype. Slogan: Not pity. Visibility.
HARD RULES — violating any of these makes the draft unusable:
- Every number about the system must come verbatim from the FACTS block below; if it's not there, don't state it.
- Product CTAs must match FACTS product status exactly. Only items marked LIVE may link to checkout; WAITLIST items must say "join the waitlist". Consulting ($200/$399/$699) is live via email application.
- Scenario language only (bullish/neutral/bearish); no buy/sell advice; no guaranteed returns; no "real-time data" claims; no personal holdings; use "high research priority" never "high conviction".
- End with: "Research & education only. Not investment advice."
- First line: "# {title}". Second line: "DRAFT — requires Mickey approval before publishing."
FACTS:
{facts[:6000]}"""
    log = {"run_at": now.isoformat(), "topic": slug, "dry_run": args.dry_run, "owner": "LOCAL-DUAL-ENGINE"}
    cp = subprocess.run([HERMES, "-z", prompt], capture_output=True, text=True, timeout=900)
    draft = cp.stdout.strip() if cp.returncode == 0 else ""
    if not draft:
        log["error"] = "hermes generation failed"
        _write_log(log, now)
        print("hermes generation failed")
        return 1
    problems = [p for p in FORBIDDEN if re.search(p, draft, re.I)]
    log["lint_problems"] = problems
    status = "NEEDS_FIX" if problems else "DRAFT"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    out = DRAFTS / f"DRAFT_{now.date().isoformat()}_{slug}.md"
    out.write_text(draft)
    log["output"] = str(out)
    _write_log(log, now)
    print(f"{status}: {out.name} lint_problems={len(problems)}")
    if not args.dry_run:
        msg = f"Weekly content draft ready: {out.name} ({status}, {len(problems)} lint flags). Review in public-content/drafts/. Not published anywhere."
        subprocess.run([HERMES, "send", "-t", "telegram"], input=msg, capture_output=True, text=True, timeout=120)
    return 0


def _write_log(log, now):
    LOGDIR.mkdir(parents=True, exist_ok=True)
    (LOGDIR / f"weekly_content-{now.date().isoformat()}.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
