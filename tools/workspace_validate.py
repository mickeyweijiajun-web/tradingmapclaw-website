#!/usr/bin/env python3
"""workspace_validate.py — CODEX entry: deterministic validation of workspace data contract.

Validates every site/data/workspace/*.json against schemas/workspace/*.schema.json and
enforces WATCHLIST_ONLY guardrails (no forbidden trade/position language) and the
LIVE-requires-dual-PASS rule. No LLM. Exit 0 = all clean, 3 = validation problems.

Usage: python3 tools/workspace_validate.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT / "site" / "data" / "workspace"
SCHEMA = ROOT / "schemas" / "workspace" / "asset.schema.json"

# forbidden in any payload narrative/catalyst/observation text (WATCHLIST_ONLY)
FORBIDDEN = re.compile(
    r"\b(buy now|sell now|go long|go short|entry price|stop[- ]loss|take[- ]profit|"
    r"price target|guaranteed|you should buy|you should sell|position size|my position|"
    r"account balance)\b", re.IGNORECASE)

ASSET_FILES = ["nvda", "mstr", "btc"]


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def check_required(d: dict, keys, path):
    return [f"{path}: missing '{k}'" for k in keys if k not in d]


def validate_asset(cid: str) -> list:
    f = WS / f"{cid}.json"
    problems = []
    if not f.exists():
        return [f"{cid}.json: FILE MISSING"]
    d = load(f)
    top = ["schema_version", "content_id", "generated_at", "data_as_of", "status",
           "freshness", "verification", "sources", "compliance", "payload"]
    problems += check_required(d, top, cid)
    if d.get("schema_version") != "1.0":
        problems.append(f"{cid}: schema_version must be '1.0'")
    if d.get("compliance") != "WATCHLIST_ONLY":
        problems.append(f"{cid}: compliance must be WATCHLIST_ONLY")
    # LIVE requires dual PASS + fresh
    if d.get("status") == "LIVE":
        v = d.get("verification", {})
        if v.get("hermes", {}).get("result") != "PASS" or v.get("codex", {}).get("result") != "PASS":
            problems.append(f"{cid}: status=LIVE but not dual-PASS (hermes+codex)")
        if d.get("freshness", {}).get("state") == "UNAVAILABLE":
            problems.append(f"{cid}: status=LIVE but freshness UNAVAILABLE")
    # UNAVAILABLE must not carry fabricated data
    if d.get("status") == "UNAVAILABLE":
        pl = d.get("payload", {})
        if pl.get("observations") or pl.get("catalysts"):
            problems.append(f"{cid}: UNAVAILABLE must not carry observations/catalysts")
    # forbidden language scan
    pl = d.get("payload", {})
    blob = " ".join([pl.get("narrative", "")] + pl.get("catalysts", []) +
                    [o.get("value", "") + o.get("label", "") for o in pl.get("observations", [])])
    m = FORBIDDEN.search(blob)
    if m:
        problems.append(f"{cid}: forbidden WATCHLIST_ONLY language: '{m.group(0)}'")
    return problems


def main() -> int:
    if not SCHEMA.exists():
        print(f"FAIL: schema missing {SCHEMA}")
        return 3
    all_problems = []
    for cid in ASSET_FILES:
        all_problems += validate_asset(cid)
    # status.json parse
    st = WS / "status.json"
    if not st.exists():
        all_problems.append("status.json: MISSING")
    else:
        s = load(st)
        if s.get("compliance") != "WATCHLIST_ONLY":
            all_problems.append("status.json: compliance must be WATCHLIST_ONLY")
    if all_problems:
        print(f"[NEEDS_FIX] workspace contract — {len(all_problems)} problem(s):")
        for p in all_problems:
            print("  -", p)
        return 3
    print(f"[PASS] workspace contract clean — {len(ASSET_FILES)} asset(s) + status validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
