#!/usr/bin/env python3
"""
build_site_data.py — TradingMapClaw static site data injector.

Reads site/data/radar-latest.json and site/data/site-config.json and injects
their values into HTML files between TMC marker comments, e.g.:

    <!--TMC:latest-update-->2026-07-12<!--/TMC:latest-update-->

Design goals (per docs/SPEC_SITE_PHASE2.md):
  - stdlib only, python3.9 compatible
  - idempotent: running twice produces zero further changes
  - --check mode: exit non-zero if any target file would change (no writes)
  - safe: only touches text strictly between matching TMC markers

Usage:
    python3 tools/build_site_data.py            # rebuild in place
    python3 tools/build_site_data.py --check     # dry run, exit 1 if stale

Marker keys currently supported (values sourced from radar-latest.json /
site-config.json, see MARKER_SOURCES below):
  latest-update, next-publication, radar-period, radar-as-of,
  radar-sample-badge, footer-date, cta-headline
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
DATA_DIR = SITE_DIR / "data"

RADAR_DATA_FILE = DATA_DIR / "radar-latest.json"
SITE_CONFIG_FILE = DATA_DIR / "site-config.json"

# Files that may contain TMC markers. Adding a new page with markers just
# means adding its path here.
TARGET_FILES = [
    SITE_DIR / "index.html",
    SITE_DIR / "radar.html",
    SITE_DIR / "products.html",
    SITE_DIR / "story.html",
    SITE_DIR / "faq.html",
    SITE_DIR / "deep-analysis.html",
    SITE_DIR / "thank-you.html",
    SITE_DIR / "get-access.html",
    SITE_DIR / "404.html",
    SITE_DIR / "system" / "index.html",
    SITE_DIR / "build-log" / "index.html",
    SITE_DIR / "research" / "index.html",
    SITE_DIR / "research" / "radar" / "index.html",
    SITE_DIR / "research" / "market-structure" / "index.html",
    SITE_DIR / "research" / "engine-disagreements" / "index.html",
    SITE_DIR / "research" / "methods" / "index.html",
    SITE_DIR / "checklist.html",
    SITE_DIR / "consulting.html",
]

CTA_COPY = {
    "A": "Get the weekly radar brief",
    "B": "See what 100+ jobs found this week",
}

MARKER_RE_TEMPLATE = r"<!--TMC:{key}-->.*?<!--/TMC:{key}-->"


def load_json(path: Path) -> dict:
    if not path.exists():
        print(f"WARNING: missing data file: {path}", file=sys.stderr)
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def next_monday_after(date_str: str) -> str:
    """Given an ISO date, return the following Monday's human-readable date.

    If the date itself is a Monday, returns the Monday 7 days later
    (i.e. "next" publication after the one on that date).
    """
    d = _dt.date.fromisoformat(date_str)
    days_ahead = (7 - d.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    nxt = d + _dt.timedelta(days=days_ahead)
    return nxt.strftime("%A, %B %-d, %Y") if hasattr(nxt, "strftime") else nxt.isoformat()


def _format_human_date(d: _dt.date) -> str:
    # %-d is not portable on all platforms (e.g. Windows); build manually.
    return f"{d.strftime('%A, %B')} {d.day}, {d.year}"


BAND_RENDER = {
    "high-research-priority": ("sf sf-hi", "high priority"),
    "watch": ("sf sf-mid", "watch"),
    "logged": ("sf sf-low", "logged"),
}


def render_radar_rows(radar_data: dict) -> str:
    """Render table <tr> rows from radar JSON (verified rows first, by |move| desc)."""
    rows = radar_data.get("rows") or []
    ok = sorted((r for r in rows if "surge_5d_pct" in r),
                key=lambda r: -abs(r["surge_5d_pct"]))
    na = [r for r in rows if "surge_5d_pct" not in r]
    out = []
    for r in ok:
        pct = r["surge_5d_pct"]
        cls = "up" if pct >= 0 else "down"
        sign = "+" if pct >= 0 else ""
        bcls, blbl = BAND_RENDER.get(r.get("band", "logged"), ("sf sf-low", "logged"))
        out.append(
            f'<tr><td class="mono"><b>{r["ticker"]}</b></td><td>{r["sector"]}</td>'
            f'<td class="{cls}">{sign}{pct}%</td><td><span class="{bcls}">{blbl}</span></td>'
            f'<td>{r.get("verified_by", "")}</td></tr>')
    for r in na:
        out.append(
            f'<tr><td class="mono"><b>{r.get("ticker", "?")}</b></td><td>{r.get("sector", "")}</td>'
            f'<td colspan="3" class="mono">DATA_UNAVAILABLE — {r.get("reason", "")}</td></tr>')
    return "\n          ".join(out)


def compute_markers(radar_data: dict, site_config: dict) -> dict:
    published_at = radar_data.get("published_at", "")
    is_sample = bool(radar_data.get("is_sample", False))
    status = radar_data.get("status", "SAMPLE" if is_sample else "LIVE")

    next_pub_raw = radar_data.get("next_publication", "auto")
    if next_pub_raw == "auto" and published_at:
        base = _dt.date.fromisoformat(published_at)
        days_ahead = (7 - base.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_pub_date = base + _dt.timedelta(days=days_ahead)
        next_pub_human = _format_human_date(next_pub_date)
    elif next_pub_raw and next_pub_raw != "auto":
        next_pub_human = next_pub_raw
    else:
        next_pub_human = "TBD"

    sample_badge = "SAMPLE — illustrative only" if is_sample else ""

    cta_variant = site_config.get("cta_variant", "A")
    cta_headline = CTA_COPY.get(cta_variant, CTA_COPY["A"])

    return {
        "latest-update": published_at or "",
        "next-publication": next_pub_human,
        "radar-period": radar_data.get("period", ""),
        "radar-as-of": radar_data.get("data_as_of", ""),
        "radar-sample-badge": sample_badge,
        "footer-date": published_at or "",
        "cta-headline": cta_headline,
        "radar-status": status,
        "radar-rows": render_radar_rows(radar_data),
        "radar-scope": radar_data.get("scope_note", ""),
    }


def apply_markers(text: str, markers: dict) -> str:
    for key, value in markers.items():
        pattern = MARKER_RE_TEMPLATE.format(key=re.escape(key))
        replacement = f"<!--TMC:{key}-->{value}<!--/TMC:{key}-->"
        text = re.sub(pattern, lambda m, r=replacement: r, text, flags=re.DOTALL)
    return text


def main() -> int:
    check_only = "--check" in sys.argv

    radar_data = load_json(RADAR_DATA_FILE)
    site_config = load_json(SITE_CONFIG_FILE)
    markers = compute_markers(radar_data, site_config)

    changed_files = []
    missing_files = []

    for path in TARGET_FILES:
        if not path.exists():
            missing_files.append(path)
            continue
        original = path.read_text(encoding="utf-8")
        updated = apply_markers(original, markers)
        if updated != original:
            changed_files.append(path)
            if not check_only:
                path.write_text(updated, encoding="utf-8")

    if missing_files:
        for p in missing_files:
            print(f"NOTE: target file does not exist yet, skipped: {p.relative_to(REPO_ROOT)}")

    if check_only:
        if changed_files:
            print("STALE — the following files need rebuilding:")
            for p in changed_files:
                print(f"  - {p.relative_to(REPO_ROOT)}")
            return 1
        print("OK — all target files up to date.")
        return 0

    if changed_files:
        print("Updated:")
        for p in changed_files:
            print(f"  - {p.relative_to(REPO_ROOT)}")
    else:
        print("No changes — already up to date (idempotent).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
