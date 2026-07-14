# TradingMapClaw — Final Handoff (2026-07-14)

> **Purpose.** This is the single authoritative record of the Perplexity → Hermes/Codex handoff.
> It captures P0/P1/P2 results, the new ownership map, the Mac production state (with SHA + Test 6/7),
> LaunchAgent status, the Workspace evidence, commit/CI/Preview/Prod/rollback pointers, degradation
> behavior, OWNER_ACTION items, BLOCKED reasons, and the shortest "continue" commands for Hermes/Codex.
>
> **Compliance:** WATCHLIST_ONLY. Research & education only. Not investment advice. The handoff does
> **not** touch trading/order/broker/execution modules, `memory.sqlite`, the scheduler, or `stocks.yaml`.

Status vocabulary used throughout: **PASS / NEEDS_FIX / BLOCKED / OWNER_ACTION**.

---

## 0. TL;DR

| Phase | Scope | Result |
|---|---|---|
| **P0** | Recover Mac loose ends (weekly_content v2, Test 6/7, owner map, date drift, idempotency, GitHub takeover test, secrets, prod regression) | **PASS** (Test 7 now fully PASS after Owner's interactive bootstrap) |
| **P1** | Formal takeover acceptance (fixed roles, state machine, degradation, health check, E2E rehearsal) | **PASS** |
| **P2a** | Workspace Lite skeleton **shipped to Production** (data contract + deterministic build + ≥1 verified asset + CI gate) | **PASS**, live |
| **P2b** | Workspace **dual-engine workflow takeover** (Hermes candidate → Codex verify → CI → Preview E2E rehearsal) | **PASS** (rehearsed 2026-07-14; fixture never reached Production) |
| **P3** | Merge/author the authoritative handoff docs + reconcile state machine | **PASS** (docs merged, PR #3) |

> **Shipping vs. workflow-takeover are separated on purpose.** P2a = the pages exist and serve on
> Production. P2b = the *process* that produces/verifies/publishes those pages is proven runnable by
> Hermes+Codex+CI without Perplexity. Both are now PASS with distinct evidence.

**The system no longer depends on Perplexity to run.** Content generation runs on the Mac (Hermes),
verification/publishing runs through GitHub Actions + Cloudflare Pages (Codex), and health monitoring
runs as a GitHub Actions workflow. After this acceptance, **one** Perplexity scheduled task remains
(daily brief), **retained as a human-optional fallback — left enabled but not auto-triggered by this
system** — because its local delivery is not yet wired (see §5). It is an OWNER_ACTION / DEFERRED item,
not an automated takeover. The weekly-content task was deleted after its Mac chain passed Test 7.

---

## 1. P0 results — Mac production close-out

### P0-B — weekly_content v2 atomic replacement — PASS
- Installed to Mac production: `/Users/mikicourage/TradingMapClaw/ops_migration/weekly_content.py`
- New SHA256 prefix: `b1b8ef…` · v1 backup: `ops_migration/weekly_content.py.v1.bak.20260714` (SHA `08bbb1…`)
- Verified: syntax, idempotency, 2-round fix loop, `.lintreport.json` sidecar, CTA present, perms preserved.
- Rollback: restore the `.v1.bak.20260714` file in place.

### P0-C — Round-3 Test 6 / Test 7
- **Test 6 — PASS.** Real `launchctl kickstart` of `ai.tmc.weekly_content`: fix loop ran exactly
  `initial(3) → fix-1(3) → fix-2(0)` (2 rounds, no infinite loop), wrote
  `DRAFT_2026-07-14_method-note.md` (7122 B), exit 0, `out.log: DRAFT ... lint_problems=0 (fix_iterations=2)`.
- **Test 6b — PASS (idempotent).** Re-trigger → `SKIP: already terminal today`, draft mtime unchanged.
- **Test 7 — PASS (final, 2026-07-14 12:0x CST).** The Owner ran `bootstrap` in the Mac's own Terminal;
  `launchctl print gui/501/ai.tmc.weekly_content` is now visible (calendarinterval trigger Mon 09:30).
  A safe `launchctl kickstart -k` then produced real evidence: **runs 0 → 1, last exit code = 0**,
  new log line `DRAFT: DRAFT_2026-07-14_method-note.md lint_problems=0 (fix_iterations=2)`, artifact on
  disk at `public-content/drafts/DRAFT_2026-07-14_method-note.md` (7122 B, marked "requires Mickey
  approval before publishing", not published anywhere), err.log empty. Re-trigger →
  `SKIP: already terminal today` (idempotent). The earlier `pc`-session `bootstrap error 5` was a
  launchd gui/501 non-interactive limit only; resolved by the Owner's interactive bootstrap. **No
  OWNER_ACTION remains for Test 7.**
  - (Historical, now DONE) The one-time interactive bootstrap command was:
    `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.tmc.weekly_content.plist`

### P0-D — Perplexity scheduled-task owner mapping — PASS
See §5 for the full table. Net (as of 2026-07-14): 2 tasks retired (GitHub health earlier; weekly
content now), **1 retained** as an OWNER-decided fallback (daily brief).

### P0-E — Date-drift fix (home / Radar / RSS / Archive from one JSON source) — PASS
- New deterministic, idempotent tool `tools/backfill_radar_meta.py` backfilled required metadata into
  `site/data/radar-latest.json`: `content_id=radar-2026-W29, week=29,
  generated_at=2026-07-13T00:00:00+08:00, schema_version=1.0, compliance=WATCHLIST_ONLY`
  (display dates unchanged).
- `tools/build_site_data.py compute_markers()` remains the **single date source** (reads
  `published_at`/`data_as_of`/`next_publication` from `radar-latest.json`); `--check` is idempotent.

### P0-F — Publish idempotency — PASS
Single LIVE edition, RSS GUID = permalink `{BASE}/research/radar/{slug}` (week-unique), archive refuses
SAMPLE editions (`is_sample` guard), Preview never writes Production.

### P0-G — Minimal GitHub takeover test — PASS
Branch → CI (verify-all gate) → Cloudflare Pages Preview → prod-smoke → revert path all exercised via PR #1.

### P0-H — Secrets scan + Production regression — PASS
Secrets scan CLEAN. Production all paths 200 (`/`, `/products`, `/skills/`, `/radar`, `/rss.xml`,
`/sitemap.xml`, `/llms.txt`, `/api/health`, `/faq`, `/story`).

**verify-all baseline: 25 PASS / 0 FAIL / 0 WARN / 3 SKIP** (3 SKIP = network smoke, run with `--smoke`).

---

## 2. P1 results — formal takeover acceptance — PASS

- **Fixed roles** (see §3): Hermes = MAKER (low-cost generation + orchestration); Codex = CHECKER +
  PUBLISHER (code / independent verification / CI / deploy / rollback).
- **State machine** reconciled — see §4. Public JSON now uses the canonical labels.
- **Degradation behavior** (see §6) verified: read-only bypass, DATA_UNAVAILABLE on source mismatch,
  no LIVE publish without dual-PASS.
- **Lightweight health check** — `tools/weekly_health.py` (non-LLM, fail-open) → `STATUS: OK`. Also runs
  as GitHub Actions `weekly-health.yml` (`30 1 * * 1` UTC = 09:30 Beijing), notify-on-change via issue.
- **E2E rehearsal — PASS.** Hermes SAMPLE fixture → Codex verify-all 25 PASS with fixture → archive guard
  **refuses SAMPLE** (`refusing to archive a SAMPLE edition`, rc=1) → secrets clean → cleanup (fixture
  removed, branches deleted, Production `radar-2026-W29` + `radar-latest` untouched) → final main
  verify-all 25 PASS / 0 FAIL. Fixture never reached Production.

---

## 3. New ownership (summary — full matrix in SYSTEM_OWNERSHIP_MATRIX.md)

| Engine / Service | Role |
|---|---|
| **Hermes** (Mac, launchd) | MAKER — generate drafts (weekly content, daily brief), orchestrate |
| **Codex** (GitHub + local) | CHECKER + PUBLISHER — code, independent verification, CI, deploy, rollback |
| **GitHub Actions** | CI gate (verify-all + workspace gates) + weekly health |
| **Cloudflare Pages** | Hosting (Preview per PR, Production on main) |
| **Owner (Mickey)** | Payments, refunds, 2FA, terms acceptance, banking, account ownership, launchd GUI bootstrap |

---

## 4. Content state machine (reconciled)

The prior `DUAL_ENGINE_PROTOCOL.md` used `HERMES_PASS / CODEX_PASS / APPROVED-CANDIDATE / PUBLISHED`.
The Workspace data contract uses a finer-grained, canonical set. **Canonical labels going forward:**

```
DRAFT → HERMES_READY → CODEX_VERIFYING → APPROVED_CANDIDATE → PREVIEW → LIVE → ARCHIVED
            │                  │
            └─ NEEDS_FIX ◀──────┘   (max 2 fix rounds, then BLOCKED)
```

Equivalence with the older labels (both are accepted in historical records):

| Canonical (new) | Legacy (DUAL_ENGINE_PROTOCOL v1) |
|---|---|
| `HERMES_READY` | `HERMES_PASS` |
| `CODEX_VERIFYING` | (implicit — Codex review in progress) |
| `APPROVED_CANDIDATE` | `APPROVED-CANDIDATE` |
| `PREVIEW` | (implicit — CF Pages PR preview) |
| `LIVE` | `PUBLISHED` |
| `ARCHIVED` | `ARCHIVED` |

**Gate rule:** `LIVE` requires **both** Hermes = PASS and Codex = PASS **and** freshness = FRESH.
Enforced deterministically by `tools/workspace_validate.py` and the radar publish pipeline.

---

## 5. Perplexity scheduled tasks — disposition

Judgement discipline: **only real run logs count as "taken over."**

| # | Task | Old owner | New owner | Disposition |
|---|---|---|---|---|
| 1 | Daily market brief | Perplexity `9b9748d6` | LOCAL-DUAL-ENGINE (`ai.tmc.daily_brief`) | **DEFERRED / OWNER_ACTION — NOT auto-taken-over.** The Mac agent is bootstrapped (runs=8, exit 0) and independently verifies, but delivery is **not** wired: today `sent=False` (`VERIFICATION FAILED — not sending` on ETH/BTC cross-source mismatch — correct graceful degradation, it refuses to send unverified numbers). Because delivery is unwired, this step is **not** part of the automated pipeline. The Perplexity task `9b9748d6` is **retained as a human-optional fallback, left enabled but not auto-triggered by this system** — it must not be recorded as PASS or auto-running. Owner decides when to wire local delivery and then delete `9b9748d6`. |
| 2 | Weekly content + Substack draft | Perplexity `d87c574c` | LOCAL-DUAL-ENGINE (`ai.tmc.weekly_content`) | **RETIRED — DELETED 2026-07-14.** Mac v2 chain passed Test 7 (runs→1, exit 0, DRAFT produced, idempotent). Per the no-dual-run rule the Perplexity task was deleted after real PASS. |
| 3 | Weekly GitHub health check | Perplexity `5196e484` | GITHUB-ACTIONS `weekly-health.yml` | **RETIRED.** 1:1 replaced; Perplexity task deleted (earlier). |

To cancel the retained fallback task later, the Owner opens the owning conversation at
`https://www.perplexity.ai/computer/tasks/<session_id>` (task #1 `9b9748d6` lives in session
`ca8fd1cc-…`) and deletes it. This system does not and must not trigger it automatically.

---

## 6. Degradation behavior (graceful)

- **Mac offline** → serve last-known-good; mark freshness `DELAYED`; no crash.
- **Data source mismatch** (>1.5% cross-source or one source down) → `DATA_UNAVAILABLE`, never guess.
- **Engine failure** (Hermes or Codex not PASS) → no `LIVE` publish; content stays `NEEDS_FIX`/`BLOCKED`.
- **CI/CF failure** → deploy blocked by verify-all gate; Production stays last-known-good.
- **Notify failure** → keep the primary artifact (draft/JSON); notification is best-effort.
- **Production regression** → immediately restore last-known-good (see ROLLBACK below).

---

## 7. P2 Workspace evidence

**P2a — shipped to Production:**
- 9 pages under `/workspace` (index, radar, research, catalysts, methodology, status, assets/{nvda,mstr,btc}).
- Data contract: `schemas/workspace/asset.schema.json` + `site/data/workspace/{nvda,mstr,btc,status}.json`.
- Tools: `tools/workspace_validate.py` (Codex gate), `tools/workspace_build.py` (idempotent generator).
- Only **NVDA is LIVE** (dual-PASS + dual-source + FRESH). MSTR/BTC are Coming soon (no fabricated data).
- CI extended: workspace validate + build-idempotency gates.
- **P2-H feature flag OFF** — no user DB, login, payment backend, or live-LLM. Reserved sections only.
- Does **not** touch home / Products / Skills / Radar / RSS / Payhip.
- **Live on Production** (post-deploy 2026-07-14, CF `3ada9478` = commit `8a82d49`): `/workspace`,
  `/workspace/assets/nvda`, `/workspace/status` all **200**.

**P2b — dual-engine workflow takeover (E2E rehearsal, 2026-07-14):**
- New executable **Codex entry point** committed: `tools/codex_verify_candidate.py` (PR #5, main `85ddf6c`).
  Exit 0 = `APPROVED_CANDIDATE`, 3 = `NEEDS_FIX`, 4 = `BLOCKED`.
- Full flow rehearsed with a synthetic fixture (`TESTZ`, not a real security):
  Hermes candidate (`HERMES_READY`) → Codex verify (`APPROVED_CANDIDATE`, rc0) → GitHub CI verify PASS
  → Cloudflare Preview `e84b58d7` → smoke. Two negative tests confirmed the gate bites:
  red-line language → `BLOCKED` (rc4); missing field → `NEEDS_FIX` (rc3).
- **Fixture never reached Production:** `/workspace/assets/testz` = **404** on both Preview and Production;
  the fixture JSON lived only in `e2e_evidence/` (never in `site/data/workspace/`, never rendered).
  PR #4 was **closed without merging**, branch deleted, fixture files removed. Production unchanged
  (`/workspace/assets/nvda` 200, `/` 200).

---

## 8. Commit / CI / Preview / Prod / rollback pointers

| Item | Value |
|---|---|
| Repo | `mickeyweijiajun-web/tradingmapclaw-website` |
| P0-E merge | PR #1 (squash) → main; CI + Deploy success; Prod smoke 10/10 |
| P2 merge | PR #2 (squash) → main `37a2bb9`; CI + Deploy success; Prod regression all 200 |
| P3 merge | PR #3 (squash) → main `8a82d49`; **run 29304453358 = success**; CF Production **`3ada9478` = commit `8a82d49`**; post-deploy 9/9 endpoints **200** |
| Codex entry point | PR #5 (squash) → main **`85ddf6c`**; CI verify + deploy PASS |
| E2E rehearsal | PR #4 **closed, not merged**; CF Preview `e84b58d7`; fixture 404 on Prod |
| Rollback branch | `final/perplexity-handoff-20260713 @ efb9a9c` (last-known-good) |
| Current main HEAD | `85ddf6c` |
| Commit identity | `git -c user.name="Mickey Wei" -c user.email="mickeyweijiajun@gmail.com"` |
| Production site | https://www.tradingmapclaw.com |
| Manual CF preview | `pip install blake3 && python3 tools/pages_deploy.py --branch <b>` with `custom-cred:api.cloudflare.com` (account `984e275d…`, project `tradingmapclaw`) |

---

## 9. OWNER_ACTION items (only these need a human)

1. ~~Test 7 bootstrap~~ — **DONE** by the Owner on 2026-07-14 (interactive Terminal bootstrap; verified
   runs=1, exit 0). No longer pending.
2. **Daily brief delivery — OWNER_ACTION / DEFERRED (the only open item).** The Mac `ai.tmc.daily_brief`
   agent runs and verifies but currently `sent=False` (correctly refuses to send on cross-source
   mismatch). This delivery step is **not auto-taken-over**. Perplexity task `9b9748d6` is **retained as
   a manual-optional fallback, left enabled but not auto-triggered by this system** — do not record it as
   PASS or auto-running. Owner decides whether to wire local delivery and then delete `9b9748d6`.
3. Payments / refunds / 2FA / terms acceptance / banking / account ownership — always Owner-only.

---

## 10. BLOCKED reasons (current)

- **None.** The earlier Test 7 `bootstrap`-via-`pc` limitation (launchd `gui/501` non-interactive,
  `error 5 I/O`) was resolved by the Owner's interactive bootstrap and verified with a real run
  (runs=1, exit 0). No BLOCKED items remain.

---

## 11. Shortest "continue" commands for the next engine

**Codex (verification / CI / deploy):**
```sh
cd tmc-v3/website/tmc-site
python3 tools/tmc_ops.py verify-all            # 25 PASS expected
python3 tools/workspace_validate.py            # workspace contract
python3 tools/workspace_build.py --check       # idempotency
python3 tools/build_site_data.py --check       # date-drift guard
python3 tools/codex_verify_candidate.py <candidate.json> --report <out.json>  # independent Codex gate (0/3/4)
# publish flow: branch → PR → CI gate → CF preview → prod-smoke → merge to main
```

**Hermes (generation, on the Mac):**
```sh
launchctl kickstart -k gui/$(id -u)/ai.tmc.weekly_content   # weekly content draft
launchctl kickstart -k gui/$(id -u)/ai.tmc.daily_brief      # daily brief
# drafts land in ops_migration/logs/ and public-content/drafts/ with .lintreport.json sidecars
```

**Health (already automated):** GitHub Actions `weekly-health.yml` runs Mondays 09:30 Beijing and opens
an issue only on change.

---

*Authored by the handoff process on 2026-07-14. See also: SYSTEM_OWNERSHIP_MATRIX.md,
OPERATIONS_AFTER_PERPLEXITY.md, FINAL_ACCEPTANCE_TESTS.md, and docs/DUAL_ENGINE_PROTOCOL.md.*
