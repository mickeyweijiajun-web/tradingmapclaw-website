#!/usr/bin/env python3
"""Publish one approved public-content record through branch -> PR -> CI.

No LLM is called. The script consumes only files already placed in the approved
outbox. System build-log records may opt into GitHub auto-merge after all checks pass.
Verification-ledger records always stop at a reviewable PR.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
DEFAULT_REPO = HOME / "TradingMapClaw" / "tradingmapclaw-website"
DEFAULT_OUTBOX = HOME / "TradingMapClaw" / "public-content" / "approved"


def run(argv, cwd, capture=False):
    return subprocess.run(
        argv, cwd=cwd, check=True, text=True,
        capture_output=capture,
    )


def safe_slug(value):
    value = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    return value[:60] or "release"


def ensure_clean(repo):
    status = run(["git", "status", "--porcelain"], repo, capture=True).stdout.strip()
    if status:
        raise RuntimeError("website repository is not clean; refusing to mix unrelated changes")


def next_input(outbox, kind):
    folder = outbox / ("system-updates" if kind == "build-log" else "verification-ledgers")
    files = sorted(folder.glob("*.json")) if folder.exists() else []
    return files[0] if files else None


def validate_dependencies():
    for binary in ("git", "gh"):
        if not shutil.which(binary):
            raise RuntimeError(f"required command is missing: {binary}")
    subprocess.run(["gh", "auth", "status"], check=True, stdout=subprocess.DEVNULL)


def publish(repo, source, kind, auto_merge):
    data = json.loads(source.read_text(encoding="utf-8"))
    content_id = data.get("content_id", source.stem)
    branch = "automation/{}".format(safe_slug(content_id))
    ensure_clean(repo)
    run(["git", "fetch", "origin", "main"], repo)
    run(["git", "switch", "-C", branch, "origin/main"], repo)
    try:
        run([sys.executable, "tools/public_release.py", kind, str(source), "--apply"], repo)
        run([sys.executable, "-m", "py_compile", *[str(p) for p in sorted((repo / "tools").glob("*.py"))]], repo)
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], repo)
        run([sys.executable, "tools/tmc_ops.py", "verify-all", "--skip-network"], repo)
        run([sys.executable, "tools/workspace_validate.py"], repo)
        run([sys.executable, "tools/workspace_build.py", "--check"], repo)
        changed = run(["git", "status", "--porcelain"], repo, capture=True).stdout.strip()
        if not changed:
            print("NO_CHANGE", content_id)
            return None
        run(["git", "add", "site/data/build-log.json", "site/data/verification-ledger-latest.json", "site/data/verification-ledger"], repo)
        run(["git", "commit", "-m", f"publish: {content_id}"], repo)
        run(["git", "push", "-u", "origin", branch], repo)
        title = "Publish {}".format(data.get("title", content_id))[:120]
        body = (
            "Automated public-content release.\n\n"
            f"- Content id: `{content_id}`\n"
            f"- Type: `{data.get('content_type')}`\n"
            "- Local unit, workspace and verify-all gates passed.\n"
            "- Research and education only; WATCHLIST_ONLY.\n"
        )
        pr_url = run([
            "gh", "pr", "create", "--base", "main", "--head", branch,
            "--title", title, "--body", body,
        ], repo, capture=True).stdout.strip()
        print("PR", pr_url)
        if auto_merge:
            if kind != "build-log":
                raise RuntimeError("auto-merge is allowed only for deterministic system build-log updates")
            run(["gh", "pr", "merge", "--auto", "--squash", pr_url], repo)
            print("AUTO_MERGE_ARMED", pr_url)
        return pr_url
    finally:
        subprocess.run(["git", "switch", "main"], cwd=repo, check=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("build-log", "verification-ledger"))
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    ap.add_argument("--outbox", type=Path, default=DEFAULT_OUTBOX)
    ap.add_argument("--prepare", action="store_true", help="run the zero-token intake step first")
    ap.add_argument("--auto-merge-system-log", action="store_true")
    args = ap.parse_args()
    if args.prepare:
        run([
            sys.executable, str(Path(__file__).with_name("public_intake.py")), args.kind,
            "--repo", str(args.repo), "--outbox", str(args.outbox),
        ], Path(__file__).parent)
    source = next_input(args.outbox, args.kind)
    if source is None:
        print("NO_APPROVED_INPUT")
        return 0
    validate_dependencies()
    pr = publish(args.repo, source, args.kind, args.auto_merge_system_log)
    archive = args.outbox.parent / "archive" / args.kind
    archive.mkdir(parents=True, exist_ok=True)
    source.replace(archive / source.name)
    print("ARCHIVED_INPUT", source.name, "PR" if pr else "NO_CHANGE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("PUBLIC_OUTBOX_BLOCKED:", exc, file=sys.stderr)
        raise SystemExit(4)
