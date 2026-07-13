#!/usr/bin/env python3
"""tmc_ops.py — TradingMapClaw operations CLI.

Subcommands:
  verify-all   Quality gate: run local (and optionally network) checks against
               the site/ tree and tools/ tree, print a human-readable report,
               optionally write a machine-readable JSON report, and exit with
               a status code that reflects pass/fail.

Design notes:
  - stdlib only (no third-party imports). Compatible with Python 3.9+.
  - Read-only with respect to site/ — this tool never writes into site/.
  - Every check is defensive: missing files, unreadable files, or malformed
    JSON must produce a FAIL/WARN result with a clear reason, never a crash
    or traceback. This matters because site/data/radar-latest.json and
    tools/build_site_data.py may not exist yet (another agent is building
    them concurrently) — checks that depend on them must degrade gracefully.

Exit codes:
  0 — no FAIL results (WARN/SKIP allowed)
  1 — at least one FAIL result, or the tool itself hit an unexpected error
      while trying to evaluate checks (checks themselves must not raise;
      if one does, it is caught and converted into a FAIL for that check id
      so the rest of the run can still complete).
"""

from __future__ import annotations

import argparse
import html.parser
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

# --------------------------------------------------------------------------
# Constants / fixtures (kept in sync with FACTS.md — do not hardcode drift)
# --------------------------------------------------------------------------

BASE_URL_DEFAULT = "https://www.tradingmapclaw.com"

BANNED_OLD_NUMBERS = [
    "119 jobs",
    "115 jobs",
    "500+ scripts",
    "502+ scripts",
    "93+ skills",
    "three-engine",
    "三引擎",
    "GPT-5.5",
]

BANNED_OLD_PRICES = ["$149", "$99"]

REQUIRED_PRICES_ANYWHERE = ["$19", "$49", "$79", "$200", "$399", "$699"]

ALLOWED_COUNCIL_MODELS = {
    "DeepSeek V4 Pro",
    "GLM-5.2",
    "GPT-5.6",
    "Qwen3 14B",
}

# Patterns that, if present, indicate a stray/other council-model name.
# We look for known "model-like" tokens near the word council/Council and
# flag ones not in the allow-list. This is best-effort text search, not a
# full NLP model.
KNOWN_OTHER_MODEL_TOKEN_PATTERNS = [
    re.compile(r"GPT-4(?:\.\d+)?\b"),
    re.compile(r"GPT-3(?:\.\d+)?\b"),
    re.compile(r"GPT-5\.5\b"),
    re.compile(r"GPT-5(?!\.\d)\b"),  # bare "GPT-5" not followed by a version number
    re.compile(r"\bClaude\b"),
    re.compile(r"\bGemini\b"),
    re.compile(r"\bLlama\b"),
    re.compile(r"\bMistral\b"),
    re.compile(r"DeepSeek V3\b"),
    re.compile(r"DeepSeek V2\b"),
    re.compile(r"GLM-4(?:\.\d+)?\b"),
    re.compile(r"GLM-5\.1\b"),
    re.compile(r"Qwen2\b"),
    re.compile(r"Qwen3 7B\b"),
    re.compile(r"Qwen3 32B\b"),
    re.compile(r"\bGrok\b"),
]

SECRET_PATTERNS = [
    ("sk-", re.compile(r"sk-[A-Za-z0-9]{10,}")),
    ("ghp_", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("github_pat_", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("AKIA", re.compile(r"AKIA[A-Z0-9]{12,}")),
    ("Bearer token", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{30,}")),
    ("generic-30char-secret", re.compile(r"[A-Za-z0-9]{30,}")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
# generic-30char-secret is extremely noisy (matches hashes, base64 assets,
# font URLs, etc.) so it is only used as a secondary signal — see
# check_secrets_scan for how false positives are filtered.

POSITION_LEAK_PATTERNS = [
    re.compile(r"my position", re.IGNORECASE),
    re.compile(r"我的持仓"),
    re.compile(r"账户余额"),
    re.compile(r"持仓金额"),
]

IMPERATIVE_TRADE_PATTERNS = [
    re.compile(r"you should buy", re.IGNORECASE),
    re.compile(r"sell now", re.IGNORECASE),
    re.compile(r"act now", re.IGNORECASE),
    re.compile(r"buy before", re.IGNORECASE),
]
# Education-context exemptions: lines that are clearly describing the *rule*
# rather than issuing the instruction (e.g. docs/specs, or sentences that
# explicitly negate the imperative) are exempted.
IMPERATIVE_EXEMPT_MARKERS = [
    "not investment advice",
    "never provides investment advice",
    "does not say",
    "we never say",
    "no instructions like",
    "we do not output",
    "not \"",
]

GUARANTEE_PATTERNS = [
    re.compile(r"guaranteed return", re.IGNORECASE),
    re.compile(r"can't lose", re.IGNORECASE),
    re.compile(r"cant lose", re.IGNORECASE),
    re.compile(r"beat the market", re.IGNORECASE),
    re.compile(r"稳赚"),
]
GUARANTEE_EXEMPT_MARKERS = [
    "no guaranteed", "not guaranteed", "no promise", "make no promise",
]

HIGH_CONVICTION_PATTERN = re.compile(r"high conviction", re.IGNORECASE)

DATE_PATTERN = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")

TMC_MARKER_SPAN = re.compile(r"<!--TMC:[^>]*-->.*?<!--/TMC:[^>]*-->", re.DOTALL)

PAYHIP_PLACEHOLDER_PATTERN = re.compile(r"PAYHIP_LINK:")

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_text(path: str):
    """Return (text, error). error is None on success."""
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as f:
            return f.read(), None
    except FileNotFoundError:
        return None, "file not found: {}".format(path)
    except UnicodeDecodeError as e:
        # Retry tolerant, but report as a WARN-worthy note via error message
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read(), "warning: non-utf8 bytes replaced ({})".format(e)
        except OSError as e2:
            return None, "unreadable: {}".format(e2)
    except OSError as e:
        return None, "unreadable: {}".format(e)


def list_files(root: str, exts):
    out = []
    if not os.path.isdir(root):
        return out
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if any(fn.endswith(e) for e in exts):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def rel(path: str, start: str) -> str:
    try:
        return os.path.relpath(path, start)
    except ValueError:
        return path


class Check:
    __slots__ = ("id", "status", "detail")

    def __init__(self, id_, status, detail):
        self.id = id_
        self.status = status  # PASS | FAIL | WARN | SKIP
        self.detail = detail

    def to_dict(self):
        return {"id": self.id, "status": self.status, "detail": self.detail}


class Runner:
    """Collects Check results, guarding each check function against crashes."""

    def __init__(self):
        self.checks = []

    def run(self, check_id, fn):
        try:
            status, detail = fn()
        except Exception as e:  # noqa: BLE001 - checks must never crash the run
            status, detail = "FAIL", "check raised an exception: {}: {}".format(
                type(e).__name__, e
            )
        self.checks.append(Check(check_id, status, detail))

    def add(self, check_id, status, detail):
        self.checks.append(Check(check_id, status, detail))


# --------------------------------------------------------------------------
# HTML helpers (stdlib html.parser based, no external deps)
# --------------------------------------------------------------------------

class _TagCollector(html.parser.HTMLParser):
    """Collects opening/closing tag balance for a fixed set of tag names,
    plus hrefs/srcs, img alt presence, input labelling info, title/meta/link
    presence, and viewport meta presence."""

    TRACK_BALANCE = {"div", "section", "table", "script"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.balance_stack = []
        self.balance_mismatch = []
        self.hrefs = []
        self.srcs = []
        self.has_title = False
        self.title_text = ""
        self._in_title = False
        self.meta_description = False
        self.meta_viewport = False
        self.canonical_href = None
        self.og_title = False
        self.og_description = False
        self.imgs_missing_alt = 0
        self.imgs_total = 0
        self.inputs = []  # list of dict: type, id, has_aria_label
        self.labels_for = set()
        self.script_ld_json_blobs = []
        self._in_script_ld_json = False
        self._ld_json_buf = []

    def handle_starttag(self, tag, attrs):
        self._handle_tag(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag, attrs):
        self._handle_tag(tag, attrs, self_closing=True)

    def _handle_tag(self, tag, attrs, self_closing):
        attrd = dict(attrs)
        tag_l = tag.lower()

        if tag_l in self.TRACK_BALANCE and not self_closing:
            self.balance_stack.append(tag_l)

        if tag_l == "title":
            self._in_title = True
            self.has_title = True

        if tag_l == "meta":
            name = (attrd.get("name") or "").lower()
            prop = (attrd.get("property") or "").lower()
            if name == "description":
                self.meta_description = True
            if name == "viewport":
                self.meta_viewport = True
            if prop == "og:title":
                self.og_title = True
            if prop == "og:description":
                self.og_description = True

        if tag_l == "link":
            rel_attr = (attrd.get("rel") or "").lower()
            if rel_attr == "canonical":
                self.canonical_href = attrd.get("href")
            href = attrd.get("href")
            if href:
                self.hrefs.append(href)

        if tag_l == "a":
            href = attrd.get("href")
            if href:
                self.hrefs.append(href)

        if tag_l == "script":
            src = attrd.get("src")
            if src:
                self.srcs.append(src)
            script_type = (attrd.get("type") or "").lower()
            if script_type == "application/ld+json":
                self._in_script_ld_json = True
                self._ld_json_buf = []
            # Note: the <script> tag is already pushed onto balance_stack above
            # via the generic TRACK_BALANCE handling — do not push again here.

        if tag_l == "img":
            self.imgs_total += 1
            src = attrd.get("src")
            if src:
                self.srcs.append(src)
            alt = attrd.get("alt")
            if alt is None:
                self.imgs_missing_alt += 1

        if tag_l == "input":
            self.inputs.append({
                "type": (attrd.get("type") or "text").lower(),
                "id": attrd.get("id"),
                "aria_label": attrd.get("aria-label"),
                "aria_labelledby": attrd.get("aria-labelledby"),
            })

        if tag_l == "label":
            for_ = attrd.get("for")
            if for_:
                self.labels_for.add(for_)

    def handle_endtag(self, tag):
        tag_l = tag.lower()
        if tag_l == "title":
            self._in_title = False
        if tag_l == "script" and self._in_script_ld_json:
            self._in_script_ld_json = False
            self.script_ld_json_blobs.append("".join(self._ld_json_buf))
            self._ld_json_buf = []
        if tag_l in self.TRACK_BALANCE:
            if self.balance_stack and self.balance_stack[-1] == tag_l:
                self.balance_stack.pop()
            else:
                # try to recover by searching for the matching open tag
                if tag_l in self.balance_stack:
                    # remove the last matching occurrence
                    for i in range(len(self.balance_stack) - 1, -1, -1):
                        if self.balance_stack[i] == tag_l:
                            del self.balance_stack[i]
                            break
                else:
                    self.balance_mismatch.append(tag_l)

    def handle_data(self, data):
        if self._in_title:
            self.title_text += data
        if self._in_script_ld_json:
            self._ld_json_buf.append(data)


def parse_html(text: str) -> _TagCollector:
    parser = _TagCollector()
    parser.feed(text)
    try:
        parser.close()
    except Exception:
        pass
    return parser


def strip_tmc_markers(text: str) -> str:
    """Remove content inside TMC injection markers so date-drift / stale
    checks don't flag legitimately-injected values."""
    return TMC_MARKER_SPAN.sub("", text)


# --------------------------------------------------------------------------
# Check implementations
# --------------------------------------------------------------------------

def check_py_compile(tools_dir: str):
    py_files = [f for f in list_files(tools_dir, [".py"])]
    if not py_files:
        return "WARN", "no .py files found under {}".format(tools_dir)
    import py_compile
    errors = []
    for f in py_files:
        try:
            py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError as e:
            errors.append("{}: {}".format(rel(f, tools_dir), e.msg))
        except SyntaxError as e:
            errors.append("{}: {}".format(rel(f, tools_dir), e))
    if errors:
        return "FAIL", "py_compile failed for {} file(s): {}".format(
            len(errors), "; ".join(errors)
        )
    return "PASS", "py_compile OK for {} file(s)".format(len(py_files))


def check_json_data_files(site_dir: str):
    data_dir = os.path.join(site_dir, "data")
    if not os.path.isdir(data_dir):
        return "WARN", "{} does not exist yet (expected — may be created by another agent)".format(
            rel(data_dir, site_dir)
        )
    json_files = list_files(data_dir, [".json"])
    if not json_files:
        return "WARN", "no *.json files found under {}".format(data_dir)

    bad = []
    radar_path = os.path.join(data_dir, "radar-latest.json")
    radar_note = None
    for jf in json_files:
        text, err = read_text(jf)
        if err and text is None:
            bad.append("{}: {}".format(rel(jf, data_dir), err))
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            bad.append("{}: invalid JSON ({})".format(rel(jf, data_dir), e))
            continue
        if os.path.abspath(jf) == os.path.abspath(radar_path):
            required_keys = ["period", "data_as_of", "is_sample", "rows"]
            if not isinstance(parsed, dict):
                bad.append("radar-latest.json: top-level must be an object")
            else:
                missing = [k for k in required_keys if k not in parsed]
                if missing:
                    bad.append(
                        "radar-latest.json: missing required key(s): {}".format(
                            ", ".join(missing)
                        )
                    )

    if not os.path.isfile(radar_path):
        radar_note = "radar-latest.json not present yet (expected — pending from site-data agent)"

    if bad:
        return "FAIL", "; ".join(bad) + (
            (" | " + radar_note) if radar_note else ""
        )
    if radar_note:
        return "WARN", "{} valid JSON file(s) parsed OK; {}".format(
            len(json_files), radar_note
        )
    return "PASS", "{} JSON file(s) parsed OK; radar-latest.json has required keys".format(
        len(json_files)
    )


def check_secrets_scan(site_dir: str, tools_dir: str):
    targets = list_files(site_dir, [".html", ".css", ".js", ".json", ".txt", ".xml"]) + \
        list_files(tools_dir, [".py", ".md", ".json"])
    findings = []
    for path in targets:
        text, err = read_text(path)
        if text is None:
            continue
        for label, pattern in SECRET_PATTERNS:
            if label == "generic-30char-secret":
                continue  # too noisy as a standalone signal; skip in default scan
            for m in pattern.finditer(text):
                findings.append("{} [{}]: {}".format(rel(path, os.path.dirname(site_dir) or "."), label, m.group(0)[:12] + "..."))
    if findings:
        return "FAIL", "potential secret(s) found: {}".format("; ".join(findings[:10]))
    return "PASS", "no secret-like patterns (sk-/ghp_/github_pat_/AKIA/Bearer .../private key) found in site/ or tools/"


def _all_html_texts(site_dir: str):
    out = []
    for path in list_files(site_dir, [".html"]):
        text, err = read_text(path)
        if text is not None:
            out.append((path, text))
    return out


def check_facts_drift(site_dir: str):
    hits = []
    for path, text in _all_html_texts(site_dir):
        for phrase in BANNED_OLD_NUMBERS:
            if phrase in text:
                hits.append("{}: contains banned phrase '{}'".format(rel(path, site_dir), phrase))
    if hits:
        return "FAIL", "; ".join(hits)
    return "PASS", "no banned legacy numbers/phrases found across {} HTML file(s)".format(
        len(list_files(site_dir, [".html"]))
    )


def check_price_drift(site_dir: str):
    hits = []
    all_text_by_page = {}
    for path, text in _all_html_texts(site_dir):
        all_text_by_page[path] = text
        for bad_price in BANNED_OLD_PRICES:
            if bad_price in text:
                hits.append("{}: contains banned legacy price '{}'".format(rel(path, site_dir), bad_price))
    if hits:
        return "FAIL", "; ".join(hits)

    combined = "\n".join(all_text_by_page.values())
    missing_required = [p for p in REQUIRED_PRICES_ANYWHERE if p not in combined]
    if missing_required:
        return "WARN", "required current price(s) not found anywhere in site/: {}".format(
            ", ".join(missing_required)
        )
    return "PASS", "no banned legacy prices; all required current prices ({}) present".format(
        ", ".join(REQUIRED_PRICES_ANYWHERE)
    )


def check_model_roster(site_dir: str):
    hits = []
    for path, text in _all_html_texts(site_dir):
        if "council" not in text.lower():
            continue
        for pattern in KNOWN_OTHER_MODEL_TOKEN_PATTERNS:
            m = pattern.search(text)
            if m:
                hits.append("{}: found disallowed model token '{}' on a council-mentioning page".format(
                    rel(path, site_dir), m.group(0)
                ))
    if hits:
        return "FAIL", "; ".join(hits)
    return "PASS", "no disallowed council model names found; allowed roster = {}".format(
        ", ".join(sorted(ALLOWED_COUNCIL_MODELS))
    )


def _resolve_clean_url(candidate: str):
    """Resolve a Cloudflare-Pages-style clean URL to a file on disk.
    Tries, in order: exact path, path+'.html', path/index.html.
    Returns the resolved path if found, else None.
    """
    if os.path.isfile(candidate):
        return candidate
    if not candidate.endswith(".html") and os.path.isfile(candidate + ".html"):
        return candidate + ".html"
    if os.path.isdir(candidate):
        idx = os.path.join(candidate, "index.html")
        if os.path.isfile(idx):
            return idx
    return None


def check_internal_links(site_dir: str):
    broken = []
    checked = 0
    for path, text in _all_html_texts(site_dir):
        parser = parse_html(text)
        page_dir = os.path.dirname(path)
        for href in parser.hrefs + parser.srcs:
            if not href:
                continue
            if href.startswith("#"):
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*:", href):
                # scheme present (http:, https:, mailto:, tel:, data:) -> external, skip
                continue
            if href.startswith("//"):
                continue
            # strip query/fragment
            clean = href.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            checked += 1
            if clean.startswith("/"):
                candidate = os.path.join(site_dir, clean.lstrip("/"))
            else:
                candidate = os.path.join(page_dir, clean)
            candidate = os.path.normpath(candidate)
            if _resolve_clean_url(candidate) is None:
                broken.append("{}: -> {} (resolved: {})".format(
                    rel(path, site_dir), href, rel(candidate, site_dir)
                ))
    if broken:
        return "FAIL", "{} broken internal link(s) of {} checked: {}".format(
            len(broken), checked, "; ".join(broken[:15])
        )
    return "PASS", "{} internal link(s) checked, all resolve to existing files (clean-URL aware: tries exact path, +'.html', /index.html)".format(checked)


def check_html_structure(site_dir: str):
    problems = []
    html_files = list_files(site_dir, [".html"])
    for path in html_files:
        text, err = read_text(path)
        if text is None:
            problems.append("{}: unreadable ({})".format(rel(path, site_dir), err))
            continue
        parser = parse_html(text)
        page_problems = []
        if parser.balance_stack or parser.balance_mismatch:
            leftover = parser.balance_stack + parser.balance_mismatch
            page_problems.append("unbalanced tag(s): {}".format(", ".join(sorted(set(leftover)))))
        if not parser.has_title or not parser.title_text.strip():
            page_problems.append("missing/empty <title>")
        if not parser.meta_description:
            page_problems.append("missing meta description")
        if not parser.meta_viewport:
            page_problems.append("missing viewport meta")
        if page_problems:
            problems.append("{}: {}".format(rel(path, site_dir), "; ".join(page_problems)))
    if problems:
        return "FAIL", "{} of {} HTML file(s) have structural issues: {}".format(
            len(problems), len(html_files), " | ".join(problems)
        )
    return "PASS", "{} HTML file(s) balanced with title/meta-description/viewport".format(len(html_files))


def check_canonical(site_dir: str, base_url: str):
    problems = []
    html_files = list_files(site_dir, [".html"])
    expected_prefix = base_url.rstrip("/") + "/"
    for path in html_files:
        text, err = read_text(path)
        if text is None:
            problems.append("{}: unreadable".format(rel(path, site_dir)))
            continue
        parser = parse_html(text)
        if not parser.canonical_href:
            problems.append("{}: no rel=canonical".format(rel(path, site_dir)))
        elif not parser.canonical_href.startswith(expected_prefix) and \
                parser.canonical_href.rstrip("/") + "/" != expected_prefix:
            problems.append("{}: canonical '{}' does not start with {}".format(
                rel(path, site_dir), parser.canonical_href, expected_prefix
            ))
    if problems:
        return "FAIL", "{} of {} page(s) missing/incorrect canonical: {}".format(
            len(problems), len(html_files), "; ".join(problems)
        )
    return "PASS", "all {} HTML page(s) have canonical starting with {}".format(
        len(html_files), expected_prefix
    )


def check_sitemap(site_dir: str, base_url: str):
    sitemap_path = os.path.join(site_dir, "sitemap.xml")
    text, err = read_text(sitemap_path)
    if text is None:
        return "FAIL", "sitemap.xml missing or unreadable: {}".format(err)

    urls_in_sitemap = re.findall(r"<loc>(.*?)</loc>", text)
    if not urls_in_sitemap:
        return "FAIL", "sitemap.xml has no <loc> entries"

    non_www = [u for u in urls_in_sitemap if "tradingmapclaw.com" in u and "www.tradingmapclaw.com" not in u]
    if non_www:
        return "FAIL", "sitemap.xml contains non-www URL(s): {}".format(", ".join(non_www))

    exempt = {"404.html", "thank-you.html"}
    html_files = list_files(site_dir, [".html"])
    missing = []
    for path in html_files:
        relp = rel(path, site_dir)
        base = os.path.basename(relp)
        if base in exempt:
            continue
        # Build slug the way this repo's URLs work: drop .html, "index.html" -> dir root
        slug = relp[:-len(".html")] if relp.endswith(".html") else relp
        if slug.endswith("/index"):
            slug = slug[: -len("index")]
        slug = slug.replace(os.sep, "/")
        candidates = {
            base_url.rstrip("/") + "/" + slug,
            base_url.rstrip("/") + "/" + slug + "/",
            base_url.rstrip("/") + "/" + relp,
        }
        if not any(c.rstrip("/") in [u.rstrip("/") for u in urls_in_sitemap] for c in candidates):
            missing.append(relp)
    if missing:
        return "WARN", "{} page(s) not referenced in sitemap.xml (may be new pages pending): {}".format(
            len(missing), ", ".join(missing)
        )
    return "PASS", "sitemap.xml has {} URL(s), all www-domain, covers existing pages (except 404/thank-you)".format(
        len(urls_in_sitemap)
    )


def check_og_tags(site_dir: str):
    primary_pages = ["index.html", "products.html", "radar.html", "story.html", "faq.html"]
    problems = []
    missing_files = []
    for page in primary_pages:
        path = os.path.join(site_dir, page)
        text, err = read_text(path)
        if text is None:
            missing_files.append(page)
            continue
        parser = parse_html(text)
        page_problems = []
        if not parser.og_title:
            page_problems.append("missing og:title")
        if not parser.og_description:
            page_problems.append("missing og:description")
        if page_problems:
            problems.append("{}: {}".format(page, ", ".join(page_problems)))
    if missing_files:
        return "WARN", "primary page(s) not found: {}".format(", ".join(missing_files))
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "all primary pages ({}) have og:title and og:description".format(", ".join(primary_pages))


def check_payhip_links(site_dir: str):
    html_files = list_files(site_dir, [".html"])
    problems = []
    placeholder_pages = []
    payhip_link_re = re.compile(r'href="([^"]*payhip\.com[^"]*)"')
    for path in html_files:
        text, err = read_text(path)
        if text is None:
            continue
        for m in payhip_link_re.finditer(text):
            href = m.group(1)
            if not href.startswith("https://"):
                problems.append("{}: payhip link not https: {}".format(rel(path, site_dir), href))
                continue
            if "/TradingMapClaw" not in href and "/b/" not in href:
                problems.append("{}: payhip link not in /TradingMapClaw or /b/ format: {}".format(
                    rel(path, site_dir), href
                ))
        if PAYHIP_PLACEHOLDER_PATTERN.search(text):
            placeholder_pages.append(rel(path, site_dir))

    if problems:
        return "FAIL", "; ".join(problems)
    if placeholder_pages:
        # Check availability=PreOrder is present alongside placeholders
        preorder_ok = True
        preorder_problems = []
        for pp in placeholder_pages:
            text, _ = read_text(os.path.join(site_dir, pp))
            if text and "PreOrder" not in text:
                preorder_ok = False
                preorder_problems.append(pp)
        detail = "PAYHIP_LINK: placeholder(s) still present (checkout not swapped) on: {}".format(
            ", ".join(placeholder_pages)
        )
        if not preorder_ok:
            detail += " | availability=PreOrder missing on: {}".format(", ".join(preorder_problems))
        return "WARN", detail
    return "PASS", "no PAYHIP_LINK placeholders remain; all payhip.com links are https and /TradingMapClaw or /b/ format"


def check_waitlist_no_checkout(site_dir: str):
    html_files = list_files(site_dir, [".html"])
    problems = []
    found_section = False
    for path in html_files:
        text, err = read_text(path)
        if text is None:
            continue
        if "Skills Library" not in text:
            continue
        found_section = True
        # crude section extraction: from "Skills Library" to next <h2/h1/section closing
        idx = text.find("Skills Library")
        window = text[idx: idx + 6000]
        if re.search(r'href="[^"]*payhip\.com[^"]*/b/[^"]*"', window):
            problems.append("{}: Skills Library section appears to contain a payhip /b/ checkout link".format(
                rel(path, site_dir)
            ))
    if not found_section:
        return "WARN", "no 'Skills Library' section found on any page to verify"
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "Skills Library section(s) found with no payhip /b/ checkout link nearby"


def check_sample_tag(site_dir: str):
    radar_json_path = os.path.join(site_dir, "data", "radar-latest.json")
    text, err = read_text(radar_json_path)
    if text is None:
        return "WARN", "radar-latest.json not present yet — cannot verify SAMPLE tag propagation ({})".format(err)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return "FAIL", "radar-latest.json invalid JSON: {}".format(e)
    is_sample = bool(data.get("is_sample")) if isinstance(data, dict) else False
    if not is_sample:
        return "PASS", "radar-latest.json is_sample=false; SAMPLE labeling not required"

    problems = []
    for page in ("radar.html", "index.html"):
        path = os.path.join(site_dir, page)
        ptext, perr = read_text(path)
        if ptext is None:
            problems.append("{}: not found ({})".format(page, perr))
            continue
        if "SAMPLE" not in ptext:
            problems.append("{}: is_sample=true but page does not render 'SAMPLE'".format(page))
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "is_sample=true and both radar.html and index.html render 'SAMPLE'"


def check_stale_dates(site_dir: str):
    """WARN (not FAIL per spec) for dates >30 days old outside TMC markers."""
    today = datetime.now()
    warns = []
    for path, text in _all_html_texts(site_dir):
        cleaned = strip_tmc_markers(text)
        for m in DATE_PATTERN.finditer(cleaned):
            date_str = m.group(0)
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            age_days = (today - d).days
            if age_days > 30:
                warns.append("{}: stale date {} ({} days old)".format(rel(path, site_dir), date_str, age_days))
    if warns:
        # de-duplicate
        uniq = sorted(set(warns))
        return "WARN", "{} stale date occurrence(s) found (>30 days old, outside TMC markers): {}".format(
            len(uniq), "; ".join(uniq[:10])
        )
    return "PASS", "no stale (>30 day old) dates found outside TMC injection markers"


def check_position_leak(site_dir: str):
    hits = []
    for path, text in _all_html_texts(site_dir):
        for pattern in POSITION_LEAK_PATTERNS:
            if pattern.search(text):
                hits.append("{}: matched pattern '{}'".format(rel(path, site_dir), pattern.pattern))
    if hits:
        return "FAIL", "; ".join(hits)
    return "PASS", "no position/account-balance leak patterns found"


def check_imperative_trade_language(site_dir: str):
    hits = []
    for path, text in _all_html_texts(site_dir):
        lower = text.lower()
        for pattern in IMPERATIVE_TRADE_PATTERNS:
            for m in pattern.finditer(text):
                start = max(0, m.start() - 80)
                context = lower[start:m.start() + 80]
                if any(marker in context for marker in IMPERATIVE_EXEMPT_MARKERS):
                    continue
                hits.append("{}: matched '{}' near: ...{}...".format(
                    rel(path, site_dir), pattern.pattern, text[start:m.start() + 40].strip()[-60:]
                ))
    if hits:
        return "FAIL", "; ".join(hits)
    return "PASS", "no imperative trading-instruction language found (education-context exemptions applied)"


def check_guaranteed_returns(site_dir: str):
    hits = []
    for path, text in _all_html_texts(site_dir):
        lower = text.lower()
        for pattern in GUARANTEE_PATTERNS:
            for m in pattern.finditer(text):
                start = max(0, m.start() - 40)
                context = lower[start:m.start() + 40]
                if any(marker in context for marker in GUARANTEE_EXEMPT_MARKERS):
                    continue
                hits.append("{}: matched '{}'".format(rel(path, site_dir), pattern.pattern))
    if hits:
        return "FAIL", "; ".join(hits)
    return "PASS", "no guaranteed-return / can't-lose / beat-the-market language found"


def check_accessibility_basics(site_dir: str):
    problems = []
    total_imgs = 0
    missing_alt = 0
    for path, text in _all_html_texts(site_dir):
        parser = parse_html(text)
        total_imgs += parser.imgs_total
        if parser.imgs_missing_alt:
            missing_alt += parser.imgs_missing_alt
            problems.append("{}: {} img(s) missing alt".format(rel(path, site_dir), parser.imgs_missing_alt))
        for inp in parser.inputs:
            if inp["type"] in ("hidden", "submit", "button"):
                continue
            has_label = inp["id"] in parser.labels_for if inp["id"] else False
            has_aria = bool(inp["aria_label"]) or bool(inp["aria_labelledby"])
            if not has_label and not has_aria:
                problems.append("{}: <input type={}> missing label/aria-label".format(
                    rel(path, site_dir), inp["type"]
                ))
    if problems:
        return "FAIL", "{} img(s) missing alt (of {} total); details: {}".format(
            missing_alt, total_imgs, "; ".join(problems[:15])
        )
    return "PASS", "all {} <img> have alt; all form inputs have label or aria-label".format(total_imgs)


def check_mobile_basics(css_path: str, site_dir: str):
    problems = []
    for path, text in _all_html_texts(site_dir):
        parser = parse_html(text)
        if not parser.meta_viewport:
            problems.append("{}: missing viewport meta".format(rel(path, site_dir)))
    css_text, css_err = read_text(css_path)
    has_media = bool(css_text and "@media" in css_text)
    if not has_media:
        problems.append("{}: no @media rule found in site.css".format(rel(css_path, site_dir)))
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "all pages have viewport meta; site.css contains @media rules"


def check_build_site_data_idempotent(tools_dir: str, site_dir: str, repo_root: str):
    script_path = os.path.join(tools_dir, "build_site_data.py")
    if not os.path.isfile(script_path):
        return "WARN", "tools/build_site_data.py does not exist yet (expected — pending from another agent)"
    import subprocess
    try:
        proc = subprocess.run(
            [sys.executable, script_path, "--check"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as e:
        return "FAIL", "failed to execute build_site_data.py --check: {}: {}".format(type(e).__name__, e)
    if proc.returncode == 0:
        return "PASS", "build_site_data.py --check exited 0 (idempotent / up to date)"
    return "FAIL", "build_site_data.py --check exited {} (rebuild needed or script error). stderr: {}".format(
        proc.returncode, (proc.stderr or "").strip()[:500]
    )


def check_llms_txt(site_dir: str):
    problems = []
    for fname in ("llms.txt", "llms-full.txt"):
        path = os.path.join(site_dir, fname)
        text, err = read_text(path)
        if text is None:
            problems.append("{}: missing or unreadable ({})".format(fname, err))
            continue
        if "v2.0" not in text:
            problems.append("{}: missing 'v2.0'".format(fname))
        if "118" not in text:
            problems.append("{}: missing '118'".format(fname))
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "llms.txt and llms-full.txt exist and contain 'v2.0' and '118'"


def check_robots_txt(site_dir: str):
    path = os.path.join(site_dir, "robots.txt")
    text, err = read_text(path)
    if text is None:
        return "FAIL", "robots.txt missing or unreadable: {}".format(err)
    if "sitemap.xml" not in text.lower():
        return "FAIL", "robots.txt does not reference sitemap.xml"
    return "PASS", "robots.txt exists and references sitemap.xml"


def check_404_page(site_dir: str):
    path = os.path.join(site_dir, "404.html")
    if not os.path.isfile(path):
        return "FAIL", "site/404.html does not exist"
    text, err = read_text(path)
    if text is None:
        return "FAIL", "404.html unreadable: {}".format(err)
    return "PASS", "site/404.html exists and is readable"


def check_site_config(site_dir: str):
    path = os.path.join(site_dir, "data", "site-config.json")
    text, err = read_text(path)
    if text is None:
        return "WARN", "site/data/site-config.json not present yet (expected — pending from another agent)"
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return "FAIL", "site-config.json invalid JSON: {}".format(e)
    if not isinstance(data, dict):
        return "FAIL", "site-config.json top-level must be an object"
    problems = []
    cta = data.get("cta_variant")
    if cta not in ("A", "B"):
        problems.append("cta_variant must be 'A' or 'B', got: {!r}".format(cta))
    ae = data.get("analytics_enabled")
    if not isinstance(ae, bool):
        problems.append("analytics_enabled must be a JSON boolean, got: {!r}".format(ae))
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "site-config.json valid: cta_variant={!r}, analytics_enabled={!r}".format(cta, ae)


# ---- network checks (opt-in via --smoke) --------------------------------

def _http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "tmc-verify-all/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - fixed scheme, controlled URL
        status = resp.status if hasattr(resp, "status") else resp.getcode()
        body = resp.read().decode("utf-8", errors="replace")
        return status, body


def check_smoke_pages(base_url: str):
    pages = ["/", "/products.html", "/radar.html", "/story.html", "/faq.html"]
    problems = []
    for p in pages:
        url = base_url.rstrip("/") + p
        try:
            status, _ = _http_get(url)
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:
            problems.append("{}: request failed: {}: {}".format(url, type(e).__name__, e))
            continue
        if status != 200:
            problems.append("{}: HTTP {}".format(url, status))
    if problems:
        return "FAIL", "; ".join(problems)
    return "PASS", "all {} primary page(s) returned HTTP 200".format(len(pages))


def check_smoke_homepage_content(base_url: str):
    url = base_url.rstrip("/")
    try:
        status, body = _http_get(url)
    except Exception as e:
        return "FAIL", "request to {} failed: {}: {}".format(url, type(e).__name__, e)
    if status != 200:
        return "FAIL", "homepage returned HTTP {}".format(status)
    if "Dual-Engine" not in body:
        return "FAIL", "homepage missing 'Dual-Engine'"
    for phrase in BANNED_OLD_NUMBERS:
        if phrase in body:
            return "FAIL", "homepage contains banned legacy phrase '{}'".format(phrase)
    return "PASS", "live homepage contains 'Dual-Engine' and no banned legacy numbers"


def check_smoke_canonical_domain(base_url: str):
    url = base_url.rstrip("/")
    try:
        status, body = _http_get(url)
    except Exception as e:
        return "FAIL", "request to {} failed: {}: {}".format(url, type(e).__name__, e)
    m = re.search(r'rel="canonical"\s+href="([^"]+)"', body)
    if not m:
        m = re.search(r"rel='canonical'\s+href='([^']+)'", body)
    if not m:
        return "FAIL", "no canonical link found on live homepage"
    canonical = m.group(1)
    expected = base_url.rstrip("/") + "/"
    if canonical.rstrip("/") + "/" != expected:
        return "FAIL", "live canonical '{}' does not match base-url '{}'".format(canonical, expected)
    return "PASS", "live canonical '{}' matches base-url domain".format(canonical)


# --------------------------------------------------------------------------
# verify-all orchestration
# --------------------------------------------------------------------------

def cmd_verify_all(args):
    repo_root = os.getcwd()
    site_dir = os.path.abspath(args.site_dir)
    tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    css_path = os.path.join(site_dir, "assets", "site.css")
    base_url = args.base_url.rstrip("/")

    runner = Runner()

    runner.run("01_py_compile", lambda: check_py_compile(tools_dir))
    runner.run("02_json_data_files", lambda: check_json_data_files(site_dir))
    runner.run("03_secrets_scan", lambda: check_secrets_scan(site_dir, tools_dir))
    runner.run("04_facts_drift", lambda: check_facts_drift(site_dir))
    runner.run("05_price_drift", lambda: check_price_drift(site_dir))
    runner.run("06_model_roster", lambda: check_model_roster(site_dir))
    runner.run("07_internal_links", lambda: check_internal_links(site_dir))
    runner.run("08_html_structure", lambda: check_html_structure(site_dir))
    runner.run("09_canonical", lambda: check_canonical(site_dir, base_url))
    runner.run("10_sitemap", lambda: check_sitemap(site_dir, base_url))
    runner.run("11_og_tags", lambda: check_og_tags(site_dir))
    runner.run("12_payhip_links", lambda: check_payhip_links(site_dir))
    runner.run("13_waitlist_no_checkout", lambda: check_waitlist_no_checkout(site_dir))
    runner.run("14_sample_tag", lambda: check_sample_tag(site_dir))
    runner.run("15_stale_dates", lambda: check_stale_dates(site_dir))
    runner.run("16_position_leak", lambda: check_position_leak(site_dir))
    runner.run("17_imperative_trade_language", lambda: check_imperative_trade_language(site_dir))
    runner.run("18_guaranteed_returns", lambda: check_guaranteed_returns(site_dir))
    runner.run("19_accessibility_basics", lambda: check_accessibility_basics(site_dir))
    runner.run("20_mobile_basics", lambda: check_mobile_basics(css_path, site_dir))
    runner.run("21_build_site_data_idempotent", lambda: check_build_site_data_idempotent(tools_dir, site_dir, repo_root))
    runner.run("22_llms_txt", lambda: check_llms_txt(site_dir))
    runner.run("23_robots_txt", lambda: check_robots_txt(site_dir))
    runner.run("24_404_page", lambda: check_404_page(site_dir))
    runner.run("25_site_config", lambda: check_site_config(site_dir))

    if args.smoke and not args.skip_network:
        runner.run("26_smoke_pages_200", lambda: check_smoke_pages(base_url))
        runner.run("27_smoke_homepage_content", lambda: check_smoke_homepage_content(base_url))
        runner.run("28_smoke_canonical_domain", lambda: check_smoke_canonical_domain(base_url))
    else:
        reason = "network checks skipped (pass --smoke to enable)" if not args.smoke else \
            "network checks skipped (--skip-network was set)"
        runner.add("26_smoke_pages_200", "SKIP", reason)
        runner.add("27_smoke_homepage_content", "SKIP", reason)
        runner.add("28_smoke_canonical_domain", "SKIP", reason)

    summary = {"pass": 0, "fail": 0, "warn": 0, "skip": 0}
    for c in runner.checks:
        summary[c.status.lower()] += 1
    overall = "FAIL" if summary["fail"] > 0 else "PASS"

    report = {
        "as_of": now_iso(),
        "base_url": base_url,
        "site_dir": rel(site_dir, repo_root),
        "checks": [c.to_dict() for c in runner.checks],
        "summary": {"pass": summary["pass"], "fail": summary["fail"], "warn": summary["warn"]},
        "overall": overall,
    }
    # keep skip count too, even though the spec's summary schema only lists pass/fail/warn
    report["summary"]["skip"] = summary["skip"]

    print_human_report(report)

    if args.json:
        try:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                f.write("\n")
        except OSError as e:
            print("ERROR: failed to write JSON report to {}: {}".format(args.json, e), file=sys.stderr)
            return 1

    return 1 if overall == "FAIL" else 0


def print_human_report(report):
    print("=" * 78)
    print("TMC verify-all report — as_of {}".format(report["as_of"]))
    print("base-url: {}   site-dir: {}".format(report["base_url"], report["site_dir"]))
    print("=" * 78)
    for c in report["checks"]:
        marker = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN", "SKIP": "SKIP"}[c["status"]]
        print("[{:>4}] {:<32} {}".format(marker, c["id"], c["detail"]))
    print("-" * 78)
    s = report["summary"]
    print("Summary: {} PASS, {} FAIL, {} WARN, {} SKIP  ->  OVERALL: {}".format(
        s["pass"], s["fail"], s["warn"], s.get("skip", 0), report["overall"]
    ))
    print("=" * 78)


# --------------------------------------------------------------------------
# argument parsing
# --------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(prog="tmc_ops.py", description="TradingMapClaw operations CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    va = sub.add_parser("verify-all", help="Run the full quality gate against the site")
    va.add_argument("--json", default=None, help="Path to write machine-readable JSON report")
    va.add_argument("--site-dir", default="site", help="Path to the site directory (default: site)")
    va.add_argument("--base-url", default=BASE_URL_DEFAULT, help="Canonical base URL (default: %(default)s)")
    va.add_argument("--skip-network", action="store_true", help="Force-skip network checks even if --smoke is set")
    va.add_argument("--smoke", action="store_true", help="Enable network smoke checks (26-28)")
    va.set_defaults(func=cmd_verify_all)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
