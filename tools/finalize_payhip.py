#!/usr/bin/env python3
"""One-shot pipeline: paste 5 Payhip URLs -> live site with real buy links.

Usage (run from tmc-site/, inside the Computer sandbox with the Cloudflare
credential preset `custom-cred:api.cloudflare.com` active):

    python3 tools/finalize_payhip.py --links-file PASTE_LINKS_HERE.txt
    python3 tools/finalize_payhip.py --tutorial-01 URL ... --patterns URL
    python3 tools/finalize_payhip.py --links-file f.txt --dry-run   # no writes

Pipeline:
  1. read + validate 5 URLs (format, non-empty, no duplicates)
  2. verify each URL is reachable (HTTP < 400)
  3. tools/swap_payhip_links.py (auto-backup + HTML sanity check)
  4. git commit
  5. deploy to Cloudflare Pages preview branch, smoke-test preview
  6. deploy to production branch (main), smoke-test https://www.tradingmapclaw.com
  7. print final status; on any failure: stop, print rollback instructions

Notes:
  * Deploy uses the documented flow in handoff/WEBSITE_MAINTENANCE.md via
    deploy-tool/pages_upload.py (expects the Cloudflare API credential to be
    injected by the sandbox HTTPS proxy — do NOT hardcode tokens here).
  * Outside the sandbox, set CF_API_TOKEN yourself and adapt _cf_headers().
"""
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent          # repo root
SITE_DIR = REPO_DIR / "site"                                # static site
WEBSITE_DIR = REPO_DIR                                      # kept for compat
ACCOUNT = "984e275d2928a92b9602542421828fcb"
PROJECT = "tradingmapclaw"
PROD_URL = "https://www.tradingmapclaw.com"
SLOT_KEYS = ["tutorial-01", "tutorial-02", "tutorial-03", "bundle-49", "patterns-79"]
ARG_MAP = {"tutorial-01": "tutorial-01", "tutorial-02": "tutorial-02",
           "tutorial-03": "tutorial-03", "bundle-49": "bundle", "patterns-79": "patterns"}


def run(cmd, cwd=None, check=True):
    print(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd or REPO_DIR, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout[-2000:])
    if r.returncode != 0:
        print(r.stderr[-2000:])
        if check:
            sys.exit(f"FAILED at: {' '.join(cmd)}")
    return r


def head_ok(url, timeout=20):
    req = urllib.request.Request(url, method="GET",
                                 headers={"User-Agent": "TMC-finalize/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except Exception as e:
        print(f"  unreachable: {url} ({e})")
        return False


def read_links_file(path):
    links = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            if k.strip() in SLOT_KEYS:
                links[k.strip()] = v.strip()
    return links


def cf_deploy(branch):
    """Deploy site/ to Cloudflare Pages via tools/pages_deploy.py (direct upload)."""
    cp = subprocess.run(["python3", str(REPO_DIR / "tools" / "pages_deploy.py"),
                         "--branch", branch], cwd=REPO_DIR,
                        capture_output=True, text=True, timeout=900)
    print(cp.stdout[-800:])
    if cp.returncode != 0:
        sys.exit(f"Cloudflare deployment failed: {cp.stderr[-400:]}")
    m = re.search(r"final url: (\S+)", cp.stdout)
    return {"url": m.group(1) if m else None, "id": "see-log"}


def smoke(base):
    pages = ["/", "/products", "/faq", "/radar", "/legal/refund"]
    ok = True
    for p in pages:
        good = head_ok(base + p)
        print(f"  {'OK ' if good else 'FAIL'} {base + p}")
        ok = ok and good
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--links-file")
    for k in ARG_MAP.values():
        ap.add_argument(f"--{k}", metavar="URL")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-url-check", action="store_true",
                    help="skip live-reachability check (rehearsals only)")
    a = ap.parse_args()

    links = read_links_file(a.links_file) if a.links_file else {}
    for slot, arg in ARG_MAP.items():
        v = getattr(a, arg.replace("-", "_"))
        if v:
            links[slot] = v.strip()

    missing = [k for k in SLOT_KEYS if not links.get(k)]
    if missing:
        sys.exit(f"Missing links for: {', '.join(missing)} — need all 5.")
    if len(set(links.values())) != 5:
        sys.exit("Duplicate URLs across slots — every product needs its own link.")
    for k, u in links.items():
        if not re.match(r"^https://payhip\.com/b/[A-Za-z0-9]+$", u):
            sys.exit(f"{k}: '{u}' is not an https://payhip.com/b/ link")

    print("== 1/6 verifying Payhip URLs are live ==")
    if a.skip_url_check:
        print("  (skipped — rehearsal mode)")
    else:
        bad = [u for u in links.values() if not head_ok(u)]
        if bad:
            sys.exit(f"Unreachable product pages (is the product published?): {bad}")

    print("== 2/6 swapping links ==")
    cmd = ["python3", "tools/swap_payhip_links.py"]
    for slot, u in links.items():
        cmd += [f"--{ARG_MAP[slot]}", u]
    if a.dry_run:
        cmd.append("--dry-run")
    run(cmd)
    if a.dry_run:
        print("DRY-RUN complete — nothing committed or deployed.")
        return

    print("== 3/6 git commit ==")
    run(["git", "add", "site/products.html"], cwd=REPO_DIR)
    run(["git", "commit", "-m", "products: go live — real Payhip buy links (5/5)"])

    print("== 4/6 preview deploy ==")
    prev = cf_deploy("payhip-golive-preview")
    time.sleep(25)
    if prev.get("url") and not smoke(prev["url"]):
        sys.exit("Preview smoke test failed — production NOT touched. "
                 "Rollback: python3 tools/swap_payhip_links.py --rollback")

    print("== 5/6 production deploy ==")
    cf_deploy("main")
    time.sleep(25)

    print("== 6/6 production smoke test ==")
    if not smoke(PROD_URL):
        sys.exit("PRODUCTION smoke test failed — investigate immediately. "
                 "Previous deployment can be restored from the Cloudflare Pages UI.")

    print("\nALL DONE ✅  5 real buy links are live at "
          f"{PROD_URL}/products — status pill now 'Instant download'.")


if __name__ == "__main__":
    main()
