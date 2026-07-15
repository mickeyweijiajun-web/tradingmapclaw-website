#!/usr/bin/env python3
"""Validate and stage public build-log or verification-ledger releases.

The script is deterministic and uses no LLM or external API. It is the only writer for
the two public JSON feeds introduced in v2.2. Research ledgers still require explicit
Hermes PASS + Codex PASS and are never auto-merged by this script.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlparse

try:
    from simple_schema import validate as validate_schema
except ModuleNotFoundError:
    from tools.simple_schema import validate as validate_schema

ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = ROOT / "site" / "data"
SCHEMAS = ROOT / "schemas" / "public"

FORBIDDEN = re.compile(
    r"\b((?:you should|you must|we recommend|consider)\s+(?:buy|sell|hold|short)|"
    r"(?:buy|sell|short)\s+(?:now|today|before|at)|go long|go short|"
    r"entry (?:price|level|at)|stop[- ]?loss|take[- ]?profit|price target|target price|"
    r"position size|my position|account balance|guaranteed (?:return|profit)|"
    r"risk[- ]?free (?:return|profit)|act now|before the market|high conviction)\b",
    re.IGNORECASE,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def schema_for(kind: str):
    name = "system_update.schema.json" if kind == "build-log" else "verification_ledger.schema.json"
    return load(SCHEMAS / name)


def compliance_errors(data, kind: str):
    errors = []
    blob = json.dumps(data, ensure_ascii=False)
    match = FORBIDDEN.search(blob)
    if match:
        errors.append(f"forbidden public-language token: {match.group(0)!r}")
    if data.get("compliance") != "WATCHLIST_ONLY":
        errors.append("compliance must be WATCHLIST_ONLY")
    if kind == "verification-ledger":
        try:
            age = (dt.datetime.now(dt.timezone.utc).date() - dt.date.fromisoformat(data["data_as_of"])).days
            if age < 0:
                errors.append("data_as_of is in the future")
            if age > 7:
                errors.append(f"verification ledger is stale ({age} days; maximum 7)")
        except (KeyError, TypeError, ValueError):
            errors.append("data_as_of must be YYYY-MM-DD")
        for index, item in enumerate(data.get("items", []), start=1):
            hosts = {urlparse(url).hostname for url in item.get("source_urls", [])}
            hosts.discard(None)
            if len(hosts) < 2:
                errors.append(f"item {index} needs two independent source domains")
    return errors


def validate(data, kind: str):
    errors = validate_schema(data, schema_for(kind), kind)
    errors.extend(compliance_errors(data, kind))
    return errors


def apply_release(data, kind: str):
    if kind == "build-log":
        target = SITE_DATA / "build-log.json"
        feed = load(target) if target.exists() else {"schema_version": "1.0", "entries": []}
        by_id = {entry["content_id"]: entry for entry in feed.get("entries", [])}
        by_id[data["content_id"]] = data
        feed["entries"] = sorted(
            by_id.values(), key=lambda item: (item["published_date"], item["content_id"]), reverse=True
        )[:100]
        dump(target, feed)
        return [target]

    latest = SITE_DATA / "verification-ledger-latest.json"
    archive = SITE_DATA / "verification-ledger" / f"{data['data_as_of']}.json"
    dump(latest, data)
    dump(archive, data)
    return [latest, archive]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("build-log", "verification-ledger"))
    ap.add_argument("input", type=Path)
    ap.add_argument("--apply", action="store_true", help="write validated output into site/data")
    args = ap.parse_args()
    try:
        data = load(args.input)
    except Exception as exc:
        print(f"BLOCKED: invalid input JSON: {exc}")
        return 4
    errors = validate(data, args.kind)
    if errors:
        print(f"BLOCKED: {len(errors)} release problem(s)")
        for error in errors:
            print(" -", error)
        return 4
    if args.apply:
        for path in apply_release(data, args.kind):
            print("WROTE", path.relative_to(ROOT))
    else:
        print("PASS: validated; no files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
