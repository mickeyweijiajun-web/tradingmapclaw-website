# Final Acceptance Tests

As-of 2026-07-14. Every row is backed by a real run. Status ∈ {PASS, NEEDS_FIX, BLOCKED, OWNER_ACTION}.
Re-run any test with the exact command shown. Compliance: WATCHLIST_ONLY.

---

## P0 — Mac production close-out

| ID | Test | Command / evidence | Expected | Status |
|---|---|---|---|---|
| P0-B1 | weekly_content v2 installed | Mac SHA of `ops_migration/weekly_content.py` = `b1b8ef…` | matches v2 | PASS |
| P0-B2 | v1 backup exists | `ops_migration/weekly_content.py.v1.bak.20260714` SHA `08bbb1…` | present | PASS |
| P0-C6 | Test 6 real run | `launchctl kickstart -k gui/$(id -u)/ai.tmc.weekly_content` | fix loop 3→3→0, DRAFT 7122 B, exit 0 | PASS |
| P0-C6b | Test 6 idempotency | re-kickstart same day | `SKIP: already terminal today`, mtime unchanged | PASS |
| P0-C7a | Test 7 bootout | `launchctl bootout gui/$(id -u)/ai.tmc.weekly_content` | STOPPED_OK, plist valid | PASS |
| P0-C7b | Test 7 bootstrap (final) | Owner ran `launchctl bootstrap gui/501 …ai.tmc.weekly_content.plist` in Mac Terminal; then `kickstart -k` | `launchctl print` visible; runs 0→1, last exit code 0; new `DRAFT … lint_problems=0 (fix_iterations=2)`; draft on disk (not published); re-trigger `SKIP: already terminal today`; err.log empty | **PASS** |
| P0-D | Perplexity owner map | see SYSTEM_OWNERSHIP_MATRIX §B | 2 retired (GitHub health + weekly content); daily brief = DEFERRED/OWNER_ACTION, `9b9748d6` retained as manual-optional fallback (not auto-triggered) | PASS (mapping correct; daily-brief delivery itself is DEFERRED, not PASS/auto) |
| P0-E | Date drift fix | `python3 tools/backfill_radar_meta.py` (idempotent) | radar-latest.json has content_id/week/schema_version/compliance | PASS |
| P0-F | Publish idempotency | archive guard + RSS GUID week-unique | single LIVE, SAMPLE refused | PASS |
| P0-G | GitHub takeover | PR #1 branch→CI→preview→smoke | all green | PASS |
| P0-H1 | Secrets scan | grep secret patterns across tree | CLEAN | PASS |
| P0-H2 | Prod regression | 10 paths on www.tradingmapclaw.com | all 200 | PASS |

---

## P1 — Formal takeover acceptance

| ID | Test | Command / evidence | Expected | Status |
|---|---|---|---|---|
| P1-1 | Fixed roles documented | DUAL_ENGINE_PROTOCOL + FINAL_HANDOFF §3 | Hermes=MAKER, Codex=CHECKER+PUBLISHER | PASS |
| P1-2 | State machine reconciled | FINAL_HANDOFF §4 | canonical labels + legacy map | PASS |
| P1-3 | Degradation behavior | FINAL_HANDOFF §6 | 6 documented + enforced paths | PASS |
| P1-4 | Health check | `python3 tools/weekly_health.py` | `STATUS: OK` | PASS |
| P1-5 | Health automation | GitHub Actions `weekly-health.yml` | scheduled, notify-on-change | PASS |
| P1-6 | E2E rehearsal | SAMPLE fixture → verify → archive-refuse → cleanup | 25 PASS, SAMPLE refused, Prod untouched | PASS |
| P1-7 | Codex independent entry point | `tools/codex_verify_candidate.py` committed (PR #5, main `85ddf6c`); self-test on clean candidate | rc 0 = `APPROVED_CANDIDATE` | PASS |
| P1-8 | Codex gate — negative (red-line) | run verifier on candidate with WATCHLIST_ONLY-violating language | rc 4 = `BLOCKED` | PASS |
| P1-9 | Codex gate — negative (schema) | run verifier on candidate missing required field | rc 3 = `NEEDS_FIX` | PASS |
| P1-10 | Full dual-engine E2E | Hermes fixture `TESTZ` → Codex `APPROVED` → CI verify PASS → CF Preview `e84b58d7` | flow green end-to-end | PASS |
| P1-11 | Fixture never in Production | GET `/workspace/assets/testz` on Preview + Production | 404 on both; PR #4 closed unmerged, branch+files removed; `/workspace/assets/nvda` still 200 | PASS |

---

## P2 — Workspace skeleton

| ID | Test | Command / evidence | Expected | Status |
|---|---|---|---|---|
| P2-1 | Data contract valid | `python3 tools/workspace_validate.py` | PASS (3 assets + status) | PASS |
| P2-2 | Deterministic build | `python3 tools/workspace_build.py` then `--check` | idempotent | PASS |
| P2-3 | LIVE gate | NVDA dual-PASS + FRESH | renders LIVE | PASS |
| P2-4 | No fabricated data | MSTR/BTC UNAVAILABLE | Coming soon, 0 tables | PASS |
| P2-5 | CI gate extended | `.github/workflows/ci.yml` | workspace validate + build --check | PASS |
| P2-6 | Sitemap updated | `grep -c workspace site/sitemap.xml` | 9 | PASS |
| P2-7 | No regression | home/products/skills/radar/rss on Prod | all 200 | PASS |
| P2-8 | Feature flag OFF | no user DB/login/payment backend/live-LLM | reserved only | PASS |
| P2-9 | Prod deploy (shipping / P2a) | PR #3 → main `8a82d49`; run 29304453358 success; CF Prod `3ada9478`=`8a82d49` | post-deploy 9/9 endpoints 200 (incl. `/workspace`, `/workspace/assets/nvda`, `/workspace/status`) | PASS |
| P2-10 | Workflow takeover (P2b) | dual-engine E2E rehearsal (see P1-7…P1-11) | Hermes→Codex→CI→Preview proven; distinct from shipping | PASS |

---

## Standing regression suite (run before any publish)

```sh
cd tmc-v3/website/tmc-site
python3 tools/tmc_ops.py verify-all        # current: 26 PASS / 0 FAIL / 0 WARN / 3 SKIP
python3 tools/workspace_validate.py        # PASS
python3 tools/workspace_build.py --check   # up to date
python3 tools/build_site_data.py --check   # up to date
python3 tools/codex_verify_candidate.py <candidate.json> --report <out.json>  # Codex gate: 0=APPROVED / 3=NEEDS_FIX / 4=BLOCKED
# secrets scan:
grep -rIE "(sk-[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}|-----BEGIN|ghp_[A-Za-z0-9]{20})" site tools schemas || echo CLEAN
```

**Overall acceptance: PASS.** No BLOCKED items. Exactly **one OWNER_ACTION remains**: wire (or decide
to keep as Perplexity fallback) the Mac daily-brief local delivery, which today reports `sent=False`
because it correctly refuses to send on cross-source number mismatch. Test 7 bootstrap is now PASS
(Owner completed it interactively; verified runs=1, exit 0). P2 is recorded as two distinct PASSes:
P2a shipping to Production and P2b dual-engine workflow takeover.
