#!/usr/bin/env python3
"""Run the independent candidate verifier over the non-public CI inbox."""
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def verify_queue(inbox, reports):
    reports.mkdir(parents=True, exist_ok=True)
    candidates = sorted(inbox.glob("*.json")) if inbox.exists() else []
    if not candidates:
        print("[PASS] candidate queue empty")
        return 0
    result = 0
    verifier = ROOT / "tools" / "codex_verify_candidate.py"
    for candidate in candidates:
        report = reports / f"{candidate.stem}.report.json"
        completed = subprocess.run(
            [sys.executable, str(verifier), str(candidate), "--report", str(report)],
            check=False,
        )
        if completed.returncode == 4:
            result = 4
        elif completed.returncode != 0 and result != 4:
            result = 3
    return result


def main():
    inbox = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "candidates"
    reports = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "codex-reports"
    return verify_queue(inbox, reports)


if __name__ == "__main__":
    raise SystemExit(main())
