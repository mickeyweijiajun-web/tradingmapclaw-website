#!/usr/bin/env python3
"""
Codex independent candidate verifier — minimal executable entry point.

Role: Codex = CHECKER. This is the deterministic (no-LLM) content/finance gate that a
Hermes candidate must clear before it can advance toward LIVE. It is intentionally
independent of workspace_validate.py (which gates the 3 committed production assets):
this one takes an arbitrary candidate file so a fixture can be verified end-to-end
WITHOUT touching production data.

Input : a candidate asset JSON (Hermes output), validated against
        schemas/workspace/asset.schema.json.
Output: a structured verification report JSON (--report path) + a proposed next state.
Exit  : 0 = APPROVED_CANDIDATE (dual-PASS + FRESH + compliant + schema-valid)
        3 = NEEDS_FIX (recoverable problems)
        4 = BLOCKED   (compliance red-line hit / schema invalid)

Continue command:
  python3 tools/codex_verify_candidate.py <candidate.json> --report <out.json>
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    from simple_schema import validate as validate_schema
except ModuleNotFoundError:
    from tools.simple_schema import validate as validate_schema

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "workspace" / "asset.schema.json"

# Compliance red-lines: personalized trading language is forbidden in WATCHLIST_ONLY content.
FORBIDDEN = re.compile(
    r"\b(buy now|sell now|short it|go long|entry at|stop loss|take profit|target price|"
    r"price target|you should (buy|sell)|guaranteed|risk-free|financial advice)\b",
    re.IGNORECASE,
)

def schema_errors(candidate):
    if not SCHEMA.exists():
        return [f"schema missing: {SCHEMA}"]
    return validate_schema(candidate, json.loads(SCHEMA.read_text()), "candidate")


def validate_candidate(candidate):
    problems = []
    blockers = schema_errors(candidate)
    cid = candidate.get("content_id", "candidate")

    if FORBIDDEN.search(json.dumps(candidate, ensure_ascii=False)):
        blockers.append(f"{cid}: FORBIDDEN trading language detected (WATCHLIST_ONLY red-line)")
    if candidate.get("compliance") != "WATCHLIST_ONLY":
        blockers.append(f"{cid}: compliance must be WATCHLIST_ONLY")

    hermes = candidate.get("verification", {}).get("hermes", {}).get("result")
    if hermes != "PASS":
        problems.append(f"{cid}: hermes result must be PASS before Codex verify (got {hermes})")
    if candidate.get("freshness", {}).get("state") != "FRESH":
        problems.append(f"{cid}: candidate freshness must be FRESH")

    observations = candidate.get("payload", {}).get("observations", [])
    has_price = any("$" in str(item.get("value", "")) or
                    "close" in str(item.get("label", "")).lower()
                    for item in observations if isinstance(item, dict))
    market = candidate.get("market_data")
    if has_price and not market:
        problems.append(f"{cid}: price observation requires market_data evidence")
    if isinstance(market, dict):
        sources = market.get("sources", [])
        names = {item.get("name") for item in sources if isinstance(item, dict)}
        if len(sources) < 2 or len(names) < 2:
            problems.append(f"{cid}: market_data requires two independent sources")
        as_of = market.get("as_of")
        if candidate.get("data_as_of") != as_of:
            problems.append(f"{cid}: market_data as_of must match data_as_of")
        if candidate.get("payload", {}).get("ticker") != market.get("ticker"):
            problems.append(f"{cid}: market_data ticker must match payload ticker")
        if any(item.get("as_of") != as_of for item in sources if isinstance(item, dict)):
            problems.append(f"{cid}: market_data source dates do not match")
        values = [float(item["value"]) for item in sources
                  if isinstance(item, dict) and isinstance(item.get("value"), (int, float))]
        if len(values) >= 2:
            mean = sum(values) / len(values)
            spread = (max(values) - min(values)) / mean * 100
            tolerance = float(market.get("tolerance_pct", 1.5))
            if spread > tolerance:
                problems.append(
                    f"{cid}: market_data sources diverge {spread:.2f}% > {tolerance:.2f}%"
                )
            published = market.get("value")
            if isinstance(published, (int, float)):
                deviation = abs(float(published) - mean) / mean * 100
                if deviation > tolerance:
                    problems.append(
                        f"{cid}: published market value deviates {deviation:.2f}% from source mean"
                    )
    return problems, blockers


def main() -> int:
    ap = argparse.ArgumentParser(description="Codex independent candidate verifier")
    ap.add_argument("candidate", help="path to Hermes candidate asset JSON")
    ap.add_argument("--report", default=None, help="path to write structured verification report")
    args = ap.parse_args()

    problems, blockers = [], []
    cand_path = Path(args.candidate)

    if not SCHEMA.exists():
        blockers.append(f"schema missing: {SCHEMA}")
    if not cand_path.exists():
        blockers.append(f"candidate missing: {cand_path}")
        return _emit(args, "BLOCKED", problems, blockers, None)

    try:
        d = json.loads(cand_path.read_text())
    except Exception as e:
        blockers.append(f"candidate not valid JSON: {e}")
        return _emit(args, "BLOCKED", problems, blockers, None)

    cid = d.get("content_id", cand_path.name)
    problems, blockers = validate_candidate(d)

    v = d.get("verification", {})
    hermes = v.get("hermes", {}).get("result")
    codex_prior = v.get("codex", {}).get("result")
    fresh = d.get("freshness", {}).get("state")
    codex_result = "PASS" if not problems and not blockers else ("BLOCKED" if blockers else "NEEDS_FIX")

    # 5) LIVE-gate simulation (candidate is NOT auto-LIVE; must be dual-PASS + FRESH)
    live_eligible = (hermes == "PASS" and codex_result == "PASS" and fresh == "FRESH")

    if blockers:
        state = "BLOCKED"
    elif problems:
        state = "NEEDS_FIX"
    else:
        state = "APPROVED_CANDIDATE"  # cleared Codex; ready for PREVIEW (still not LIVE)

    return _emit(args, state, problems, blockers, {
        "content_id": cid,
        "candidate_sha256": hashlib.sha256(cand_path.read_bytes()).hexdigest(),
        "hermes": hermes,
        "codex_prior": codex_prior,
        "codex_result": codex_result,
        "freshness": fresh,
        "live_eligible": live_eligible,
    })


def _emit(args, state, problems, blockers, detail):
    report = {
        "verifier": "codex_verify_candidate",
        "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "proposed_state": state,
        "detail": detail,
        "problems": problems,
        "blockers": blockers,
    }
    line = f"[{state}] codex verify — {len(problems)} problem(s), {len(blockers)} blocker(s)"
    print(line)
    for p in problems:
        print("  - problem:", p)
    for b in blockers:
        print("  - blocker:", b)
    if detail:
        print(f"  transition: {detail['hermes']}(hermes) + {detail['codex_result']}(codex) "
              f"freshness={detail['freshness']} -> {state} (live_eligible={detail['live_eligible']})")
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2))
        print("  report:", args.report)
    return {"APPROVED_CANDIDATE": 0, "NEEDS_FIX": 3, "BLOCKED": 4}.get(state, 3)


if __name__ == "__main__":
    sys.exit(main())
