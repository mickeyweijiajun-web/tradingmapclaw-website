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

try:
    from simple_schema import validate as validate_schema
except ModuleNotFoundError:
    from tools.simple_schema import validate as validate_schema

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT / "site" / "data" / "workspace"
SCHEMA = ROOT / "schemas" / "workspace" / "asset.schema.json"

# forbidden in any payload narrative/catalyst/observation text (WATCHLIST_ONLY)
FORBIDDEN = re.compile(
    r"\b(buy now|sell now|go long|go short|entry price|stop[- ]loss|take[- ]profit|"
    r"price target|guaranteed|you should buy|you should sell|position size|my position|"
    r"account balance)\b", re.IGNORECASE)

PUBLIC_STATES = {"LIVE", "UNAVAILABLE", "ARCHIVED"}


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def check_required(d: dict, keys, path):
    return [f"{path}: missing '{k}'" for k in keys if k not in d]


def asset_ids():
    return sorted(p.stem for p in WS.glob("*.json") if p.name != "status.json")


def validate_asset(cid: str) -> list:
    f = WS / f"{cid}.json"
    problems = []
    if not f.exists():
        return [f"{cid}.json: FILE MISSING"]
    d = load(f)
    schema = load(SCHEMA)
    problems += validate_schema(d, schema, cid)
    top = ["schema_version", "content_id", "generated_at", "data_as_of", "status",
           "freshness", "verification", "sources", "compliance", "payload"]
    problems += check_required(d, top, cid)
    if d.get("schema_version") != "1.0":
        problems.append(f"{cid}: schema_version must be '1.0'")
    if d.get("compliance") != "WATCHLIST_ONLY":
        problems.append(f"{cid}: compliance must be WATCHLIST_ONLY")
    if d.get("status") not in PUBLIC_STATES:
        problems.append(f"{cid}: status={d.get('status')} is not allowed in public workspace")
    if d.get("status") != "UNAVAILABLE":
        if d.get("generated_at") is None or d.get("data_as_of") is None:
            problems.append(f"{cid}: published data requires generated_at and data_as_of")
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
    ids = asset_ids()
    for cid in ids:
        all_problems += validate_asset(cid)
    # status.json parse
    st = WS / "status.json"
    if not st.exists():
        all_problems.append("status.json: MISSING")
    else:
        s = load(st)
        if s.get("compliance") != "WATCHLIST_ONLY":
            all_problems.append("status.json: compliance must be WATCHLIST_ONLY")
        listed = {item.get("content_id", "").replace("ws-asset-", ""): item
                  for item in s.get("assets", [])}
        if set(listed) != set(ids):
            all_problems.append(
                f"status.json: assets {sorted(listed)} do not match data files {ids}"
            )
        for cid in set(listed).intersection(ids):
            asset = load(WS / f"{cid}.json")
            if listed[cid].get("status") != asset.get("status"):
                all_problems.append(f"status.json: {cid} status does not match asset file")
            if listed[cid].get("freshness") != asset.get("freshness", {}).get("state"):
                all_problems.append(f"status.json: {cid} freshness does not match asset file")
    if all_problems:
        print(f"[NEEDS_FIX] workspace contract — {len(all_problems)} problem(s):")
        for p in all_problems:
            print("  -", p)
        return 3
    print(f"[PASS] workspace contract clean — {len(ids)} asset(s) + status validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
