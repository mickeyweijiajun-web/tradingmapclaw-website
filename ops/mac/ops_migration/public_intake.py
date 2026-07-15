#!/usr/bin/env python3
"""Prepare public-release records from deterministic or pre-approved inputs.

System logs are generated from repository revision metadata without an LLM. Research
ledgers are never derived from arbitrary report text: this script only accepts the
explicit, already redacted Hermes/Codex bridge contract and revalidates it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
DEFAULT_REPO = HOME / "TradingMapClaw" / "tradingmapclaw-website"
DEFAULT_OUTBOX = HOME / "TradingMapClaw" / "public-content" / "approved"
DEFAULT_LEDGER = HOME / "shared_context" / "public_verification_ledger.json"

RELEASE_ONLY_PREFIXES = (
    "site/data/build-log.json",
    "site/data/verification-ledger-latest.json",
    "site/data/verification-ledger/",
)

CATEGORIES = (
    (".github/", "Continuous integration and deployment controls changed."),
    ("tools/", "Quality-gate or publication tooling changed."),
    ("ops/mac/", "Mac scheduling or publication automation changed."),
    ("schemas/", "A public data contract changed."),
    ("site/legal/", "A public disclosure or legal-information page changed."),
    ("site/research/", "A research-method or evidence page changed."),
    ("site/", "A public website page or feed changed."),
    ("docs/", "Operating documentation changed."),
)


def git(repo: Path, *args: str) -> str:
    cp = subprocess.run(["git", *args], cwd=repo, check=True, text=True, capture_output=True)
    return cp.stdout.strip()


def changed_paths(repo: Path) -> list[str]:
    output = git(repo, "show", "--first-parent", "--pretty=format:", "--name-only", "HEAD")
    return sorted({line.strip() for line in output.splitlines() if line.strip()})


def public_categories(paths: list[str]) -> list[str]:
    messages = []
    for prefix, message in CATEGORIES:
        if any(path.startswith(prefix) for path in paths) and message not in messages:
            messages.append(message)
    return messages[:8]


def is_release_only(paths: list[str]) -> bool:
    return bool(paths) and all(
        any(path == prefix or path.startswith(prefix) for prefix in RELEASE_ONLY_PREFIXES)
        for path in paths
    )


def seen(content_id: str, repo: Path, outbox: Path) -> bool:
    feed = repo / "site" / "data" / "build-log.json"
    if feed.exists():
        try:
            if any(item.get("content_id") == content_id
                   for item in json.loads(feed.read_text(encoding="utf-8")).get("entries", [])):
                return True
        except (OSError, ValueError):
            pass
    for root in (outbox, outbox.parent / "archive"):
        for path in root.rglob("*.json") if root.exists() else []:
            try:
                if json.loads(path.read_text(encoding="utf-8")).get("content_id") == content_id:
                    return True
            except (OSError, ValueError):
                continue
    return False


def write_and_validate(data: dict, kind: str, repo: Path, target: Path) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cp = subprocess.run(
        [sys.executable, str(repo / "tools" / "public_release.py"), kind, str(target)],
        cwd=repo, text=True, capture_output=True,
    )
    if cp.returncode:
        target.unlink(missing_ok=True)
        print(cp.stdout or cp.stderr, file=sys.stderr)
        return 4
    print("PREPARED", target)
    return 0


def prepare_system_log(repo: Path, outbox: Path) -> int:
    head = git(repo, "rev-parse", "HEAD")
    short = head[:12]
    paths = changed_paths(repo)
    if not paths or is_release_only(paths):
        print("NO_MATERIAL_SYSTEM_CHANGE")
        return 0
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    content_id = f"build-{today}-revision-{short}"
    if seen(content_id, repo, outbox):
        print("ALREADY_PREPARED", content_id)
        return 0
    categories = public_categories(paths) or ["Repository implementation or operating documentation changed."]
    data = {
        "schema_version": "1.0",
        "content_id": content_id,
        "content_type": "SYSTEM_BUILD_LOG",
        "published_date": today,
        "title": f"Automated system update: revision {short}",
        "summary": "The maintained repository advanced to a new revision. This entry reports engineering categories and quality evidence only; it makes no market claim.",
        "changes": categories,
        "evidence": [f"Repository revision {short}", "Deterministic public-release validation"],
        "status": "APPROVED",
        "compliance": "WATCHLIST_ONLY",
    }
    target = outbox / "system-updates" / f"{content_id}.json"
    return write_and_validate(data, "build-log", repo, target)


def prepare_ledger(source: Path, repo: Path, outbox: Path) -> int:
    if not source.exists():
        print("NO_PUBLIC_LEDGER_CONTRACT")
        return 0
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"BLOCKED_LEDGER: {exc}", file=sys.stderr)
        return 4
    content_id = data.get("content_id", "invalid")
    if seen(content_id, repo, outbox):
        print("ALREADY_PREPARED", content_id)
        return 0
    target = outbox / "verification-ledgers" / f"{content_id}.json"
    return write_and_validate(data, "verification-ledger", repo, target)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("build-log", "verification-ledger"))
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    ap.add_argument("--outbox", type=Path, default=DEFAULT_OUTBOX)
    ap.add_argument("--ledger-source", type=Path, default=DEFAULT_LEDGER)
    args = ap.parse_args()
    if args.kind == "build-log":
        return prepare_system_log(args.repo.expanduser(), args.outbox.expanduser())
    return prepare_ledger(args.ledger_source.expanduser(), args.repo.expanduser(), args.outbox.expanduser())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.SubprocessError) as exc:
        print("PUBLIC_INTAKE_BLOCKED:", exc, file=sys.stderr)
        raise SystemExit(4)
