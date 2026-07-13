#!/usr/bin/env python3
"""Self-contained Cloudflare Pages direct-upload deployer for tradingmapclaw.

Usage (from repo root, with Cloudflare account credentials available):
  python3 tools/pages_deploy.py --branch phase2-preview   # preview deploy
  python3 tools/pages_deploy.py --branch main             # production deploy

Auth model (two distinct tokens):
  * account token — injected by the sandbox HTTPS proxy (custom-cred) or
    CLOUDFLARE_API_TOKEN env var; used for upload-token + deployments.
  * short-lived JWT from /upload-token — used for the assets endpoints.
    These calls are made WITHOUT the proxy (proxy would override the JWT
    Authorization header with the account token → 'Authorization failed').

Never prints or persists tokens. Requires: pip install blake3
Implements wrangler's upload protocol: blake3(base64(content)+ext)[:32],
check-missing, batched upload, upsert-hashes, deployment with manifest.
"""
import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from blake3 import blake3

ACCOUNT = "984e275d2928a92b9602542421828fcb"
PROJECT = "tradingmapclaw"
API = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/pages/projects/{PROJECT}"
ASSETS = "https://api.cloudflare.com/client/v4/pages/assets"
SITE = Path(__file__).resolve().parent.parent / "site"
TOK = os.environ.get("CLOUDFLARE_API_TOKEN")  # optional; proxy usually injects


def curl(url, method="GET", headers=None, json_body=None, form=None,
         timeout=180, use_proxy=True):
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-X", method, url]
    if not use_proxy:
        cmd.insert(1, "--noproxy")
        cmd.insert(2, "*")
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    if TOK and "Authorization" not in (headers or {}):
        cmd += ["-H", f"Authorization: Bearer {TOK}"]
    tmp = None
    if json_body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(json_body, tmp)
        tmp.close()
        cmd += ["-H", "Content-Type: application/json", "--data-binary", f"@{tmp.name}"]
    for k, v in (form or {}).items():
        cmd += ["-F", f"{k}={v}"]
    env = dict(os.environ)
    if not use_proxy:
        for var in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy", "ALL_PROXY"):
            env.pop(var, None)
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30, env=env)
        if cp.returncode != 0:
            sys.exit(f"curl failed ({cp.returncode}): {cp.stderr[:300]}")
        try:
            return json.loads(cp.stdout)
        except json.JSONDecodeError:
            sys.exit(f"non-JSON response from {url}: {cp.stdout[:300]}")
    finally:
        if tmp:
            os.unlink(tmp.name)


def file_hash(data: bytes, suffix: str) -> str:
    b64 = base64.b64encode(data).decode()
    return blake3((b64 + suffix).encode()).hexdigest()[:32]


def build_manifest(root: Path):
    files = [p for p in root.rglob("*") if p.is_file() and ".bak" not in p.name
             and not any(part.startswith(".") for part in p.relative_to(root).parts)]
    if not files or len(files) > 1000:
        sys.exit(f"refusing: {len(files)} files")
    manifest, payloads = {}, {}
    for p in files:
        data = p.read_bytes()
        h = file_hash(data, p.suffix.lstrip("."))
        manifest["/" + str(p.relative_to(root))] = h
        payloads[h] = (data, mimetypes.guess_type(p.name)[0] or "application/octet-stream")
    return manifest, payloads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", required=True)
    ap.add_argument("--dir", default=str(SITE))
    a = ap.parse_args()

    manifest, payloads = build_manifest(Path(a.dir).resolve())
    print(f"{len(manifest)} files, {len(payloads)} unique hashes")

    # 1. account-auth: short-lived upload JWT
    r = curl(f"{API}/upload-token")
    if not r.get("success"):
        sys.exit(f"upload-token failed: {json.dumps(r)[:300]}")
    jwt_h = {"Authorization": f"Bearer {r['result']['jwt']}"}

    # 2. JWT-auth, direct (no proxy): check-missing / upload / upsert
    r = curl(f"{ASSETS}/check-missing", "POST", jwt_h,
             {"hashes": list(payloads)}, use_proxy=False)
    if not r.get("success"):
        sys.exit(f"check-missing failed: {json.dumps(r)[:300]}")
    missing = r["result"]
    print(f"{len(missing)} assets to upload")
    batch, size = [], 0

    def flush():
        nonlocal batch, size
        if not batch:
            return
        rr = curl(f"{ASSETS}/upload", "POST", jwt_h, batch, use_proxy=False)
        if not rr.get("success"):
            sys.exit(f"asset upload failed: {json.dumps(rr)[:300]}")
        batch, size = [], 0

    for h in missing:
        data, ctype = payloads[h]
        b64 = base64.b64encode(data).decode()
        batch.append({"key": h, "value": b64, "metadata": {"contentType": ctype}, "base64": True})
        size += len(b64)
        if len(batch) >= 40 or size > 25_000_000:
            flush()
    flush()
    if missing:
        rr = curl(f"{ASSETS}/upsert-hashes", "POST", jwt_h,
                  {"hashes": list(payloads)}, use_proxy=False)
        if not rr.get("success"):
            print(f"warn: upsert-hashes failed: {json.dumps(rr)[:200]}")

    # 3. account-auth: create deployment
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as mf:
        json.dump(manifest, mf)
        mfname = mf.name
    d = curl(f"{API}/deployments", "POST",
             form={"manifest": f"<{mfname}", "branch": a.branch}, timeout=240)
    os.unlink(mfname)
    if not d.get("success"):
        sys.exit(f"deployment failed: {json.dumps(d)[:500]}")
    res = d["result"]
    print(f"deployment id={res['id']} env={res.get('environment')} url={res.get('url')}")
    stage, st = {}, {}
    for _ in range(25):
        time.sleep(6)
        st = curl(f"{API}/deployments/{res['id']}").get("result") or {}
        stage = st.get("latest_stage") or {}
        print(f"  {stage.get('name')}: {stage.get('status')}")
        if stage.get("status") in ("success", "failure") and stage.get("name") == "deploy":
            break
    print(f"final url: {st.get('url')}")
    return 0 if stage.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
