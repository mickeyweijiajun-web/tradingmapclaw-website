#!/usr/bin/env python3
"""Swap waitlist CTAs on products.html for real Payhip buy links. (v2)

Usage:
    python3 tools/swap_payhip_links.py \
        --tutorial-01 https://payhip.com/b/AAAA \
        --tutorial-02 https://payhip.com/b/BBBB \
        --tutorial-03 https://payhip.com/b/CCCC \
        --bundle      https://payhip.com/b/DDDD \
        --patterns    https://payhip.com/b/EEEE \
        [--dry-run] [--rollback]

Safety features (v2):
  * HTTPS + payhip.com/b/ format check on every URL
  * rejects empty URLs and duplicate URLs across slots
  * automatic timestamped backup (products.html.bak-YYYYmmdd-HHMMSS)
  * --dry-run: show the would-be diff, write nothing
  * unified diff printed on every real run
  * post-swap HTML sanity check (html.parser full parse + link count)
  * flips products.html JSON-LD availability PreOrder -> InStock when all 5 swapped
  * --rollback: restore the most recent backup
"""
import argparse
import datetime
import difflib
import html.parser
import json
import re
import sys
from pathlib import Path

SLOTS = {
    "tutorial-01": ("PAYHIP_LINK:tutorial-01", "Buy now — $19"),
    "tutorial-02": ("PAYHIP_LINK:tutorial-02", "Buy now — $19"),
    "tutorial-03": ("PAYHIP_LINK:tutorial-03", "Buy now — $19"),
    "bundle": ("PAYHIP_LINK:bundle-49", "Buy the bundle — $49"),
    "patterns": ("PAYHIP_LINK:patterns-bundle", "Buy now — $79"),
}
PILL_OLD = "Ready — checkout connecting"
PILL_NEW = "Instant download"
HTML = Path(__file__).resolve().parent.parent / "site" / "products.html"


class _Check(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.payhip_links = 0

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href.startswith("https://payhip.com/b/"):
                self.payhip_links += 1


def rollback() -> int:
    baks = sorted(HTML.parent.glob("products.html.bak-*"))
    if not baks:
        print("ERROR: no backup found to roll back to")
        return 1
    HTML.write_text(baks[-1].read_text(encoding="utf-8"), encoding="utf-8")
    print(f"OK: restored {baks[-1].name} -> products.html")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    for slot in SLOTS:
        ap.add_argument(f"--{slot}", metavar="URL")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rollback", action="store_true")
    args = vars(ap.parse_args())
    if args["rollback"]:
        return rollback()

    urls = {s: (args.get(s.replace("-", "_")) or "").strip() for s in SLOTS}
    urls = {s: u for s, u in urls.items() if u}
    if not urls:
        print("Nothing to do — pass at least one --<slot> URL.")
        return 0
    dupes = [u for u in set(urls.values()) if list(urls.values()).count(u) > 1]
    if dupes:
        print(f"ERROR: duplicate URL used for multiple slots: {dupes}")
        return 1
    for slot, url in urls.items():
        if not re.match(r"^https://payhip\.com/b/[A-Za-z0-9]+$", url):
            print(f"ERROR: {slot}: '{url}' is not an https://payhip.com/b/ link")
            return 1

    text = orig = HTML.read_text(encoding="utf-8")
    changed = []
    for slot, url in urls.items():
        marker, cta = SLOTS[slot]
        if marker not in text:
            print(f"ERROR: marker '{marker}' not found in products.html")
            return 1
        pattern = re.compile(
            r"(<!--[^>]*" + re.escape(marker) + r"[^>]*-->\s*)"
            r'<div class="paypal-slot">.*?</div>',
            re.DOTALL,
        )
        replacement = (
            r"\1"
            f'<div class="paypal-slot"><a class="btn btn-primary" '
            f'href="{url}" target="_blank" rel="noopener">{cta}</a></div>'
        )
        text, n = pattern.subn(replacement, text)
        if n == 0:
            print(f"ERROR: paypal-slot after marker '{marker}' not found "
                  f"(already swapped, or markup changed)")
            return 1
        changed.append(slot)

    if len(changed) == len(SLOTS):
        text = text.replace(PILL_OLD, PILL_NEW)
        text = text.replace('"availability":"https://schema.org/PreOrder"',
                            '"availability":"https://schema.org/InStock"')

    diff = list(difflib.unified_diff(
        orig.splitlines(), text.splitlines(),
        "products.html (before)", "products.html (after)", lineterm=""))
    print("\n".join(diff[:80]) or "(no textual diff?)")
    if len(diff) > 80:
        print(f"... ({len(diff) - 80} more diff lines)")

    chk = _Check()
    chk.feed(text)
    print(f"\nHTML parse: OK · payhip buy links in result: {chk.payhip_links}")
    if chk.payhip_links != len(changed):
        print("ERROR: link count mismatch after swap — aborting write")
        return 1
    for m in [s[0] for s in SLOTS.values() if s[0].startswith("PAYHIP")]:
        pass  # markers stay in place by design (idempotence anchors)

    if args["dry_run"]:
        print("DRY-RUN: nothing written.")
        return 0

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = HTML.parent / f"products.html.bak-{stamp}"
    bak.write_text(orig, encoding="utf-8")
    HTML.write_text(text, encoding="utf-8")
    print(f"OK: swapped {len(changed)} CTA(s): {', '.join(changed)}")
    print(f"Backup: {bak.name} (restore with --rollback)")
    print("Next: git diff → git commit → redeploy Cloudflare Pages "
          "(or run tools/finalize_payhip.py to do it all)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
