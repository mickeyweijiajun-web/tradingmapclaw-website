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
| **P0** | Recover Mac loose ends (weekly_content v2, Test 6/7, owner map, date drift, idempotency, GitHub takeover test, secrets, prod regression) | **PASS** (Test 7 `bootstrap` = OWNER_ACTION — launchd GUI-domain limit) |
| **P1** | Formal takeover acceptance (fixed roles, state machine, degradation, health check, E2E rehearsal) | **PASS** |
| **P2** | Workspace Lite skeleton (data contract + deterministic build + ≥1 verified asset + CI gate) | **PASS**, live on Production |
| **P3** | Merge/author the authoritative handoff docs | **This document set** |

**The system no longer depends on Perplexity to run.** Content generation runs on the Mac (Hermes),
verification/publishing runs through GitHub Actions + Cloudflare Pages (Codex), and health monitoring
runs as a GitHub Actions workflow. Two Perplexity scheduled tasks remain only as OWNER-decided fallbacks
(see §5).

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
- **Test 7 — bootout PASS / bootstrap OWNER_ACTION.** `bootout` deactivated the agent cleanly
  (`STOPPED_OK`, plist retained + valid `plutil`). `bootstrap`/`load` returns `error 5 (I/O)` in the
  non-interactive `pc` session — this is a launchd **gui/501 domain** restriction, not a file problem.
  The plist is valid on disk and auto-loads on next login/reboot.
  - **OWNER_ACTION (run in the Mac's own Terminal):**
    ```sh
    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.tmc.weekly_content.plist
    ```

### P0-D — Perplexity scheduled-task owner mapping — PASS
See §5 for the full table. Net: 1 task retired (replaced 1:1 by GitHub Actions), 2 retained as
OWNER-decided fallbacks.

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
| 1 | Daily market brief | Perplexity `9b9748d6` | LOCAL-DUAL-ENGINE (`ai.tmc.daily_brief`) | **RETAINED (OWNER_ACTION).** Mac generates + independently verifies (13/13), but `sent=False` (no local push yet). Keep Perplexity task until local push is wired, or Owner decides to drop it. |
| 2 | Weekly content + Substack draft | Perplexity `d87c574c` | LOCAL-DUAL-ENGINE (`ai.tmc.weekly_content`) | **RETAINED (OWNER_ACTION).** Generation moved to Mac (v2, Test 6 PASS). Reminder/push retention is Owner's call. |
| 3 | Weekly GitHub health check | Perplexity `5196e484` | GITHUB-ACTIONS `weekly-health.yml` | **RETIRED.** 1:1 replaced; Perplexity task deleted. |

To cancel a retained task later, the Owner opens the owning conversation at
`https://www.perplexity.ai/computer/tasks/<session_id>` (task #1/#2 live in session `ca8fd1cc-…`).

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

- 9 pages under `/workspace` (index, radar, research, catalysts, methodology, status, assets/{nvda,mstr,btc}).
- Data contract: `schemas/workspace/asset.schema.json` + `site/data/workspace/{nvda,mstr,btc,status}.json`.
- Tools: `tools/workspace_validate.py` (Codex gate), `tools/workspace_build.py` (idempotent generator).
- Only **NVDA is LIVE** (dual-PASS + dual-source + FRESH). MSTR/BTC are Coming soon (no fabricated data).
- CI extended: workspace validate + build-idempotency gates.
- **P2-H feature flag OFF** — no user DB, login, payment backend, or live-LLM. Reserved sections only.
- Does **not** touch home / Products / Skills / Radar / RSS / Payhip.
- **Live on Production:** `/workspace`, `/workspace/assets/nvda`, `/workspace/status` all 200.

---

## 8. Commit / CI / Preview / Prod / rollback pointers

| Item | Value |
|---|---|
| Repo | `mickeyweijiajun-web/tradingmapclaw-website` |
| P0-E merge | PR #1 (squash) → main; CI + Deploy success; Prod smoke 10/10 |
| P2 merge | PR #2 (squash) → main HEAD `37a2bb9`; CI + Deploy success (58s); Prod regression all 200 |
| Rollback branch | `final/perplexity-handoff-20260713 @ efb9a9c` (last-known-good) |
| Commit identity | `git -c user.name="Mickey Wei" -c user.email="mickeyweijiajun@gmail.com"` |
| Production site | https://www.tradingmapclaw.com |
| Manual CF preview | `pip install blake3 && python3 tools/pages_deploy.py --branch <b>` with `custom-cred:api.cloudflare.com` (account `984e275d…`, project `tradingmapclaw`) |

---

## 9. OWNER_ACTION items (only these need a human)

1. **Test 7 bootstrap** — run in the Mac's own Terminal:
   `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.tmc.weekly_content.plist`
   (or simply log out/in — the valid plist auto-loads).
2. **Daily brief push** — decide whether to wire local push (`sent=False` today) or keep the Perplexity
   fallback task `9b9748d6`.
3. **Weekly content reminder** — decide retention of Perplexity task `d87c574c`.
4. Payments / refunds / 2FA / terms acceptance / banking / account ownership — always Owner-only.

---

## 10. BLOCKED reasons (current)

- **Test 7 `bootstrap` via `pc`** — launchd `gui/501` domain cannot be bootstrapped from a non-interactive
  session (`error 5 I/O`). Not a code/file fault. Resolved by the OWNER_ACTION in §9.1. No other BLOCKED items.

---

## 11. Shortest "continue" commands for the next engine

**Codex (verification / CI / deploy):**
```sh
cd tmc-v3/website/tmc-site
python3 tools/tmc_ops.py verify-all            # 25 PASS expected
python3 tools/workspace_validate.py            # workspace contract
python3 tools/workspace_build.py --check       # idempotency
python3 tools/build_site_data.py --check       # date-drift guard
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
