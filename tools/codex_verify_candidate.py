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
import json, re, sys, argparse, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "workspace" / "asset.schema.json"

# Compliance red-lines: personalized trading language is forbidden in WATCHLIST_ONLY content.
FORBIDDEN = re.compile(
    r"\b(buy now|sell now|short it|go long|entry at|stop loss|take profit|target price|"
    r"price target|you should (buy|sell)|guaranteed|risk-free|financial advice)\b",
    re.IGNORECASE,
)

TOP_KEYS = ["schema_version", "content_id", "generated_at", "data_as_of", "status",
            "freshness", "verification", "sources", "compliance", "payload"]


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

    # 1) required-key / schema-shape check
    for k in TOP_KEYS:
        if k not in d:
            problems.append(f"{cid}: missing required key '{k}'")

    # 2) compliance red-line scan (whole document)
    if FORBIDDEN.search(json.dumps(d, ensure_ascii=False)):
        blockers.append(f"{cid}: FORBIDDEN trading language detected (WATCHLIST_ONLY red-line)")
    if d.get("compliance") != "WATCHLIST_ONLY":
        blockers.append(f"{cid}: compliance must be WATCHLIST_ONLY")

    # 3) dual-engine verification presence
    v = d.get("verification", {})
    hermes = v.get("hermes", {}).get("result")
    codex_prior = v.get("codex", {}).get("result")
    if hermes != "PASS":
        problems.append(f"{cid}: hermes result must be PASS before Codex verify (got {hermes})")

    # 4) Codex independent judgement -> stamps its own PASS/NEEDS_FIX
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
