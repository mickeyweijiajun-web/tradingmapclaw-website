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
| P0-C7b | Test 7 bootstrap | `launchctl bootstrap gui/$(id -u) …plist` via `pc` | `error 5` (gui-domain limit) | OWNER_ACTION |
| P0-D | Perplexity owner map | see SYSTEM_OWNERSHIP_MATRIX §B | 1 retired, 2 retained | PASS |
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
| P2-9 | Prod deploy | PR #2 merged → main | `/workspace`, `/workspace/assets/nvda`, `/workspace/status` = 200 | PASS |

---

## Standing regression suite (run before any publish)

```sh
cd tmc-v3/website/tmc-site
python3 tools/tmc_ops.py verify-all        # 25 PASS / 0 FAIL / 0 WARN / 3 SKIP
python3 tools/workspace_validate.py        # PASS
python3 tools/workspace_build.py --check   # up to date
python3 tools/build_site_data.py --check   # up to date
# secrets scan:
grep -rIE "(sk-[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}|-----BEGIN|ghp_[A-Za-z0-9]{20})" site tools schemas || echo CLEAN
```

**Overall acceptance: PASS** (single OWNER_ACTION = Test 7 bootstrap; no BLOCKED items remaining).
