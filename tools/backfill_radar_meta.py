#!/usr/bin/env python3
"""backfill_radar_meta.py — deterministically fill required meta fields in radar-latest.json.

Fills content_id / generated_at / week / schema_version ONLY when null/missing, deriving
from existing fields (period, published_at). Display dates are untouched (they come from
published_at / data_as_of). Idempotent: re-running produces identical output.

Usage: python3 tools/backfill_radar_meta.py [--check]
  --check : exit 3 if a change WOULD be made, 0 if already complete (no write)
"""
import json
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
F = SITE / "data" / "radar-latest.json"


def derive(d: dict) -> dict:
    out = dict(d)
    period = out.get("period") or ""  # e.g. "2026-W29"
    # week number from ISO period
    if out.get("week") in (None, "", 0):
        if "-W" in period:
            try:
                out["week"] = int(period.split("-W")[1])
            except (ValueError, IndexError):
                pass
    # content_id: stable, one-LIVE-per-week key
    if not out.get("content_id"):
        out["content_id"] = f"radar-{period}" if period else "radar-unknown"
    # generated_at: fall back to published_at (date-only) when missing
    if not out.get("generated_at"):
        pub = out.get("published_at") or ""
        out["generated_at"] = f"{pub}T00:00:00+08:00" if pub else ""
    # schema contract marker
    if not out.get("schema_version"):
        out["schema_version"] = "1.0"
    if not out.get("compliance"):
        out["compliance"] = "WATCHLIST_ONLY"
    return out


def main() -> int:
    check = "--check" in sys.argv
    d = json.loads(F.read_text(encoding="utf-8"))
    new = derive(d)
    if new == d:
        print("OK — radar-latest.json meta already complete (idempotent)")
        return 0
    if check:
        changed = [k for k in new if new.get(k) != d.get(k)]
        print(f"WOULD_CHANGE: {changed}")
        return 3
    F.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    changed = [k for k in new if new.get(k) != d.get(k)]
    print(f"backfilled: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
