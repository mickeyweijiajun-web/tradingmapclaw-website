# Site Phase 2 Changelog

Scope: `site/` (all pages, assets, data), `tools/build_site_data.py` (new),
`docs/SITE_CHANGELOG_PHASE2.md` (this file). No files under `tools/tmc_ops.py`,
`tools/weekly_health.py`, or `content/` were touched, per task constraints.

Reference: `docs/SPEC_SITE_PHASE2.md`, `FACTS.md` (v2.0).

## 1. New pages

| Path | File | Purpose |
|---|---|---|
| `/system` | `site/system/index.html` | Full architecture + migrated "All-Weather Run" daily schedule (was on homepage) |
| `/research` | `site/research/index.html` | Research hub — 4 category cards + newsletter signup |
| `/research/radar` | `site/research/radar/index.html` | Market Radar archive (links to `/radar` for the live sample table) |
| `/research/market-structure` | `site/research/market-structure/index.html` | Market Structure Briefs archive (1 labeled sample entry) |
| `/research/engine-disagreements` | `site/research/engine-disagreements/index.html` | Engine Disagreement Notes archive (1 labeled sample entry) |
| `/research/methods` | `site/research/methods/index.html` | Research Method Releases archive (1 labeled sample entry) |
| `/build-log` | `site/build-log/index.html` | 3 build milestones, grounded strictly in FACTS.md figures |
| `/checklist.html` | `site/checklist.html` | Free 15-item interactive research checklist, localStorage-persisted, no server |
| `/consulting` | `site/consulting.html` | Consulting qualification form (mailto: submit, no holdings/account/password fields) |

All new pages reuse the existing nav/footer/head structure and CSS classes
from `site/index.html` / `site/assets/site.css` — verified byte-for-byte
identical `nav-links` and footer `Explore` blocks across every page (old and
new). Every page includes the WATCHLIST_ONLY compliance disclaimer.

## 2. Homepage (`site/index.html`) restructuring

- Removed a duplicated `#story` / `#who` block accidentally left at the top
  of the file from an earlier edit pass.
- Removed the "All-Weather Run" daily-schedule section from the homepage —
  migrated in full to the new `/system` page.
- Final section order now: Hero → `#coverage` → `#system` (short summary,
  links to `/system` for the full schedule) → `#latest-intelligence` →
  `#archive` → `#products-teaser` → `#consulting-teaser` → `#founder-story`
  → `#newsletter` → Footer.
- Updated nav (`Story / Research / System / Build Log / Products / FAQ`) and
  footer `Explore` column (`Research / System / Build Log / The Story / Deep
  Analysis / Products / Consulting / Free Checklist / FAQ`) — then propagated
  the same nav/footer to **every** existing page (`story.html`, `faq.html`,
  `deep-analysis.html`, `thank-you.html`, `get-access.html`, `404.html`,
  `radar.html`, `products.html`) for site-wide consistency.
- Added `data-tmc-event="github_click"` to the hero and top-bar GitHub links.

## 3. Compliance fixes

- `radar.html`: "high conviction" → "high research priority" (all occurrences).
- `site/llms-full.txt`: "🔴 High-Conviction" → "🔴 High Research Priority";
  "Kelly-criterion position sizing → BUY/HOLD/WATCH" → reworded to "Scoring
  Engine: turns a model's conviction into a numeric score, then a plain
  scenario label per ticker (illustrative, not a recommendation)"; T26 Supply
  Chain Onion description's "buy/sell" → "scenario label".
- `site/llms-full.txt`: removed a stray duplicate "$149" tutorial line (only
  the correct $19/$19/$19/$49/$79 pricing ladder remains) and reworded the
  checkout line so Lemon Squeezy is described as a **planned future backup
  checkout, not yet in use** — Payhip is stated as the current channel.
- Site-wide grep confirms zero remaining occurrences of: `high conviction`,
  `GPT-5.5`, `$149`, `$99`, `three-engine` (see §7 for the exact commands run).
- `products.html`: added the 5th `<!-- PAYHIP_LINK:bundle-49 -->` placeholder
  (previously a leftover PayPal-button block) — now 5 total placeholders:
  `tutorial-01`, `tutorial-02`, `tutorial-03`, `bundle-49`, `patterns-bundle`.
  Confirmed JSON-LD `availability` correctly splits `PreOrder` (digital
  products) vs `InStock` (consulting, which is actually live).
- `site/consulting.html`: qualification form collects name, email, problem
  description, technical level, and budget tier only — verified via grep that
  it never asks about holdings, account balances, or passwords.
- `site/checklist.html`: all 15 items are pure research-process steps; none
  contain buy/sell instructions, price targets, or position-sizing advice.

## 4. Data-driven pages (`tools/build_site_data.py`)

New stdlib-only (Python 3.9+), idempotent script. Reads
`site/data/radar-latest.json` + `site/data/site-config.json` and injects
values between `<!--TMC:key-->...<!--/TMC:key-->` markers via regex across
18 target files (see `TARGET_FILES` in the script — every page carrying a
marker, including all 5 research subpages, checklist, and consulting).

Supported markers: `latest-update`, `next-publication`, `radar-period`,
`radar-as-of`, `radar-sample-badge`, `footer-date`, `cta-headline`.

Usage:
```
python3 tools/build_site_data.py            # rebuild in place
python3 tools/build_site_data.py --check     # dry run, exit 1 if stale
```

Verified idempotent — two consecutive runs, plus `--check`, all report
"already up to date" / exit 0.

New data files: `site/data/radar-latest.json` (sample radar row data, marked
`is_sample: true` / `status: SAMPLE`), `site/data/site-config.json`
(`cta_variant`, `analytics_enabled` — both currently conservative defaults:
`"A"` and `false`).

## 5. Anonymous event tracking (`site/assets/js/tmc-events.js`)

New file. `window.tmcEvent(name, detail)`:
- When `analytics_enabled` is `false` (current default) → `console.debug`
  only. No network calls, no cookies, no fingerprinting, no third-party
  script is ever loaded.
- When `true` → lazily injects GoatCounter (a cookie-less, privacy-friendly
  analytics endpoint) and fires the event through it.
- Auto-wires every element with `data-tmc-event="..."` (click, or submit for
  `<form>` elements) plus fires a `page_view` event on load.
- Events covered: `page_view`, `newsletter_submit`, `radar_view`,
  `product_click`, `payhip_click`, `consulting_mail_click`, `github_click`.

The `<script src="/assets/js/tmc-events.js"></script>` tag was added to
**every** HTML page in `site/` (verified via grep — zero pages missing it),
including the 6 pre-existing pages that previously had no such hook
(`get-access.html`, `faq.html`, `thank-you.html`, `story.html`,
`deep-analysis.html`, `404.html`, and all 6 `site/legal/*.html` pages).

## 6. Sitemap & LLM discovery files

- `site/sitemap.xml`: added all 9 new pages (`/system`, `/research`,
  `/research/radar`, `/research/market-structure`,
  `/research/engine-disagreements`, `/research/methods`, `/build-log`,
  `/checklist.html`, `/consulting`). Also corrected pre-existing stale legal
  URLs that didn't match actual files under `site/legal/` (`refunds` →
  `refund`; removed non-existent `cookies` and `imprint` entries; added the
  missing `delivery` and `contact` legal pages). Validated as well-formed XML.
- `site/llms.txt`: added Research hub, System, Build Log, Free Checklist, and
  Consulting to both the "What it publishes" / "Products & services" section
  and the "Links" section.
- `site/llms-full.txt`: added the same 5 new page links to its "## 10. Links"
  section, in addition to the compliance fixes in §3.

## 7. Self-check results

```
$ python3 tools/build_site_data.py   # run 1
No changes — already up to date (idempotent).
$ python3 tools/build_site_data.py   # run 2
No changes — already up to date (idempotent).
$ python3 tools/build_site_data.py --check
OK — all target files up to date.
$ grep -rin "high conviction" site/      → (no output)
$ grep -rin "GPT-5\.5" site/             → (no output)
$ grep -rn '\$149' site/                → (no output)
$ grep -rn '\$99\b' site/                → (no output)
$ grep -rin "three-engine|three engine" site/ → (no output)
$ python3 -c "import xml.etree.ElementTree as ET; ET.parse('site/sitemap.xml')"  → valid
```

All 9 new page paths confirmed present in `site/sitemap.xml`. All HTML pages
site-wide confirmed to contain the `WATCHLIST_ONLY` disclaimer and the
`tmc-events.js` script tag. All new pages confirmed to use the
`https://www.tradingmapclaw.com/...` canonical form.

## 8. Constraint compliance

- Only `site/`, `tools/build_site_data.py`, and this changelog were modified.
- `tools/tmc_ops.py` and `tools/weekly_health.py` confirmed untouched
  (`git status --short tools/` shows zero diff against the last commit).
- `content/` confirmed untouched (`git status --short content/` shows zero
  diff).
- Scratch helper scripts used to generate the new pages
  (`_page_template.py`, `build_research_pages.py`, `build_buildlog_page.py`,
  `build_checklist_page.py`, `build_consulting_page.py`) were kept in
  `/home/user/workspace/scratch/`, outside the repo, since only
  `tools/build_site_data.py` is permitted as a new file under `tools/`.

## 9. Known gaps / not done

- No automated visual regression / screenshot QA was run against the new
  pages — only structural (grep/XML/idempotency) checks. A manual visual
  pass in a browser is recommended before shipping.
- `site/research/market-structure`, `/research/engine-disagreements`, and
  `/research/methods` each currently ship with exactly one clearly-labeled
  **SAMPLE** placeholder entry (no real published briefs exist yet per
  FACTS.md / content/ handoff) — these should be replaced with real entries
  as soon as that content exists.
- GoatCounter is referenced as the analytics backend in `tmc-events.js` but
  no GoatCounter account/site has been provisioned — this is inert
  (`analytics_enabled: false`) until a real account is set up and the flag
  is flipped in `site/data/site-config.json`.
- No CI wiring was added to run `tools/build_site_data.py --check`
  automatically on push — recommend adding it to the existing
  `.github/` workflows in a follow-up.
