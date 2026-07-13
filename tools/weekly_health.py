#!/usr/bin/env python3
"""weekly_health.py — TradingMapClaw weekly repo & site health check.

Checks (each is independently guarded — a failure in one never stops the
others, and never raises out of main()):
  1. GitHub repo health for mickeyweijiajun-web/tradingmapclaw-website and
     mickeyweijiajun-web/TradingMapClaw: open issues count, open PR count,
     days since latest commit. Uses GH_TOKEN env var if present (adds it as
     an Authorization header), otherwise calls the GitHub REST API
     anonymously (subject to the anonymous rate limit).
  2. HTTP status of the main pages of https://www.tradingmapclaw.com.
  3. Runs `python3 tools/tmc_ops.py verify-all --skip-network` in-process
     (via subprocess) and reports its overall PASS/FAIL.

Output: writes a markdown report to --out (default: health-report.md).
The FIRST LINE of the report is always exactly:
    STATUS: OK
    STATUS: DRIFT
    STATUS: FAIL
followed by markdown detail sections.

Fail-open contract: this script's own process exit code is ALWAYS 0
(unless argument parsing itself fails), even when STATUS is FAIL. The
calling workflow is responsible for deciding what to do based on the
STATUS line in the report — that keeps a broken network, a GitHub outage,
or a rate limit from ever breaking the weekly cron. No secrets/tokens are
ever printed to stdout/stderr or written into the report.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

GITHUB_API = "https://api.github.com"
REPOS = [
    "mickeyweijiajun-web/tradingmapclaw-website",
    "mickeyweijiajun-web/TradingMapClaw",
]
SITE_BASE_URL = "https://www.tradingmapclaw.com"
SITE_PAGES = ["/", "/products.html", "/radar.html", "/story.html", "/faq.html"]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _redact(msg: str) -> str:
    """Best-effort redaction in case an error message ever echoes a token
    (e.g. from a URL containing a query-string credential). We never build
    URLs with tokens in them, but this is a defensive backstop."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        msg = msg.replace(token, "***REDACTED***")
    return msg


def _http_json_get(url, timeout=10):
    """GET a URL and parse JSON. Returns (data, error_str). Never raises."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {
        "User-Agent": "tmc-weekly-health/1.0",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body), None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return None, _redact("HTTP {} from {}: {}".format(e.code, url, body[:200]))
    except urllib.error.URLError as e:
        return None, _redact("network error calling {}: {}".format(url, e))
    except (json.JSONDecodeError, TimeoutError, OSError) as e:
        return None, _redact("error calling {}: {}: {}".format(url, type(e).__name__, e))


def check_repo_health(repo: str):
    """Returns a dict with keys: repo, open_issues, open_prs, days_since_commit,
    error (None on success)."""
    result = {
        "repo": repo,
        "open_issues": None,
        "open_prs": None,
        "days_since_commit": None,
        "error": None,
    }

    repo_data, err = _http_json_get("{}/repos/{}".format(GITHUB_API, repo))
    if err:
        result["error"] = err
        return result
    if not isinstance(repo_data, dict):
        result["error"] = "unexpected /repos response shape"
        return result

    # GitHub's /repos/{owner}/{repo}.open_issues_count includes PRs; fetch
    # PRs separately to disambiguate.
    total_open = repo_data.get("open_issues_count")

    prs_data, prs_err = _http_json_get(
        "{}/repos/{}/pulls?state=open&per_page=100".format(GITHUB_API, repo)
    )
    if prs_err:
        result["error"] = prs_err
        # still try to report total_open as issues if PR count unavailable
        result["open_issues"] = total_open
        return result

    open_prs = len(prs_data) if isinstance(prs_data, list) else None
    if isinstance(total_open, int) and isinstance(open_prs, int):
        result["open_issues"] = max(total_open - open_prs, 0)
        result["open_prs"] = open_prs
    else:
        result["open_issues"] = total_open
        result["open_prs"] = open_prs

    commits_data, commits_err = _http_json_get(
        "{}/repos/{}/commits?per_page=1".format(GITHUB_API, repo)
    )
    if commits_err:
        # Non-fatal: keep issue/PR numbers, just leave commit age unknown.
        result["error"] = commits_err
        return result
    if isinstance(commits_data, list) and commits_data:
        date_str = (
            commits_data[0].get("commit", {}).get("committer", {}).get("date")
            or commits_data[0].get("commit", {}).get("author", {}).get("date")
        )
        if date_str:
            try:
                commit_dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc
                )
                result["days_since_commit"] = (datetime.now(timezone.utc) - commit_dt).days
            except ValueError:
                pass
    return result


def check_site_pages():
    """Returns list of dicts: {path, status, error}."""
    out = []
    for path in SITE_PAGES:
        url = SITE_BASE_URL.rstrip("/") + path
        entry = {"path": path, "status": None, "error": None}
        req = urllib.request.Request(url, headers={"User-Agent": "tmc-weekly-health/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:  # nosec
                entry["status"] = resp.status if hasattr(resp, "status") else resp.getcode()
        except urllib.error.HTTPError as e:
            entry["status"] = e.code
        except urllib.error.URLError as e:
            entry["error"] = _redact("network error: {}".format(e))
        except OSError as e:
            entry["error"] = _redact("error: {}".format(e))
        out.append(entry)
    return out


def run_verify_all(repo_root: str):
    """Runs `python3 tools/tmc_ops.py verify-all --skip-network` and returns
    (overall_str, summary_dict_or_None, error_str_or_None)."""
    tmc_ops_path = os.path.join(repo_root, "tools", "tmc_ops.py")
    if not os.path.isfile(tmc_ops_path):
        return None, None, "tools/tmc_ops.py not found at {}".format(tmc_ops_path)

    json_out = os.path.join(repo_root, ".weekly_health_verify_report.json")
    try:
        proc = subprocess.run(
            [sys.executable, tmc_ops_path, "verify-all", "--skip-network", "--json", json_out],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return None, None, "verify-all timed out after 60s"
    except Exception as e:  # noqa: BLE001
        return None, None, "failed to execute verify-all: {}: {}".format(type(e).__name__, e)

    overall = None
    summary = None
    try:
        with open(json_out, "r", encoding="utf-8") as f:
            data = json.load(f)
        overall = data.get("overall")
        summary = data.get("summary")
    except (OSError, json.JSONDecodeError) as e:
        return None, None, "verify-all ran (exit {}) but JSON report unreadable: {}".format(
            proc.returncode, e
        )
    finally:
        try:
            os.remove(json_out)
        except OSError:
            pass

    if overall is None:
        return None, None, "verify-all produced no 'overall' field (exit {}, stderr: {})".format(
            proc.returncode, (proc.stderr or "").strip()[:300]
        )
    return overall, summary, None


def build_report(repo_root: str):
    """Runs all checks defensively and returns (status, markdown_body)."""
    drift = False
    hard_fail = False
    sections = []

    # 1. GitHub repo health
    gh_lines = ["## GitHub repo health", ""]
    for repo in REPOS:
        r = check_repo_health(repo)
        if r["error"]:
            drift = True
            gh_lines.append("- **{}**: ERROR — {}".format(repo, r["error"]))
        else:
            gh_lines.append(
                "- **{}**: open issues = {}, open PRs = {}, days since latest commit = {}".format(
                    repo,
                    r["open_issues"] if r["open_issues"] is not None else "unknown",
                    r["open_prs"] if r["open_prs"] is not None else "unknown",
                    r["days_since_commit"] if r["days_since_commit"] is not None else "unknown",
                )
            )
            if isinstance(r["days_since_commit"], int) and r["days_since_commit"] > 30:
                drift = True
                gh_lines.append("  - ⚠️ no commits in {} days".format(r["days_since_commit"]))
    sections.append("\n".join(gh_lines))

    # 2. Site page status
    site_lines = ["## Site page status ({})".format(SITE_BASE_URL), ""]
    site_results = check_site_pages()
    any_site_error = False
    for entry in site_results:
        if entry["error"]:
            any_site_error = True
            site_lines.append("- `{}`: ERROR — {}".format(entry["path"], entry["error"]))
        else:
            ok = entry["status"] == 200
            if not ok:
                any_site_error = True
            site_lines.append("- `{}`: HTTP {}{}".format(
                entry["path"], entry["status"], "" if ok else "  ⚠️"
            ))
    if any_site_error:
        drift = True
    sections.append("\n".join(site_lines))

    # 3. verify-all --skip-network
    va_lines = ["## Local quality gate (verify-all --skip-network)", ""]
    overall, summary, err = run_verify_all(repo_root)
    if err:
        drift = True
        va_lines.append("- ERROR running verify-all: {}".format(err))
    else:
        va_lines.append("- overall: **{}**".format(overall))
        if summary:
            va_lines.append(
                "- summary: {} PASS, {} FAIL, {} WARN, {} SKIP".format(
                    summary.get("pass", "?"),
                    summary.get("fail", "?"),
                    summary.get("warn", "?"),
                    summary.get("skip", "?"),
                )
            )
        if overall == "FAIL":
            hard_fail = True
    sections.append("\n".join(va_lines))

    if hard_fail:
        status = "FAIL"
    elif drift:
        status = "DRIFT"
    else:
        status = "OK"

    header = "STATUS: {}".format(status)
    meta = "_Generated {} by tools/weekly_health.py_".format(now_iso())
    body = "\n\n".join([header, "# TMC Weekly Health Report", meta] + sections) + "\n"
    return status, body


def main(argv=None):
    parser = argparse.ArgumentParser(prog="weekly_health.py", description="TMC weekly health check (fail-open)")
    parser.add_argument("--out", default="health-report.md", help="Output markdown report path (default: %(default)s)")
    args = parser.parse_args(argv)

    repo_root = os.getcwd()

    try:
        status, body = build_report(repo_root)
    except Exception as e:  # noqa: BLE001 - absolute last-resort guard; must never raise
        status = "FAIL"
        body = (
            "STATUS: FAIL\n\n# TMC Weekly Health Report\n\n"
            "_Generated {}_\n\nUnexpected error while building the report: {}: {}\n"
        ).format(now_iso(), type(e).__name__, _redact(str(e)))

    try:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(body)
    except OSError as e:
        # Even failing to write the report must not break the cron.
        print("weekly_health.py: could not write {}: {}".format(args.out, e), file=sys.stderr)

    print("STATUS: {}".format(status))
    # Fail-open: this script's process exit code is always 0. The calling
    # workflow inspects the STATUS line / report file to decide next steps.
    return 0


if __name__ == "__main__":
    sys.exit(main())
