# Operations After Perplexity — Startup & Runbook

> Read this first if Perplexity is no longer available. It is the entry point for running
> TradingMapClaw with only Hermes (Mac) + Codex (GitHub/Cloudflare) + GitHub Actions.
> Compliance: WATCHLIST_ONLY · research & education only · not investment advice.

---

## 1. What runs where (no Perplexity required)

```
 ┌─────────────┐     drafts      ┌──────────────┐   PR    ┌──────────────┐  main   ┌───────────────┐
 │  HERMES      │ ─────────────▶ │  local repo   │ ──────▶ │ GitHub Actions │ ──────▶ │ Cloudflare     │
 │  (Mac,       │  weekly/daily   │  tmc-site     │  verify │  CI + health   │  deploy │ Pages (Prod)   │
 │  launchd)    │                │  (CODEX edits)│  gate   │                │         │ www.tmc.com    │
 └─────────────┘                 └──────────────┘         └──────────────┘         └───────────────┘
```

- **Generation** → Hermes on the Mac (launchd agents).
- **Verification + publish** → Codex via local tools + GitHub Actions CI + Cloudflare Pages.
- **Health** → GitHub Actions `weekly-health.yml` (self-running).

---

## 2. Daily / weekly operating loop

1. **Hermes generates** a draft (weekly content Monday, daily brief weekday mornings). Drafts land in
   `ops_migration/logs/` and `public-content/drafts/` with a `.lintreport.json` sidecar and a status.
2. **Codex verifies**: run the deterministic checks (below). Draft advances
   `HERMES_READY → CODEX_VERIFYING → APPROVED_CANDIDATE` only on dual-PASS.
3. **Publish**: create a branch → PR → CI gate → Cloudflare Preview → prod-smoke → merge to `main`.
   Merging `main` deploys Production.
4. **Archive + RSS**: on LIVE, the edition is frozen (`/research/radar/<slug>/`) and added to RSS
   (GUID = permalink). SAMPLE editions are refused by the archive guard.

---

## 3. Codex — deterministic verification (no LLM)

```sh
cd tmc-v3/website/tmc-site
python3 tools/tmc_ops.py verify-all         # expect: 25 PASS / 0 FAIL / 0 WARN / 3 SKIP
python3 tools/tmc_ops.py verify-all --smoke # add network smoke (pages 200, canonical, homepage)
python3 tools/workspace_validate.py         # workspace data contract (WATCHLIST_ONLY + LIVE gate)
python3 tools/workspace_build.py --check    # workspace pages built & idempotent
python3 tools/build_site_data.py --check    # single date source, no drift
```

All must exit 0. A non-zero exit blocks publish.

---

## 4. Hermes — trigger generation (on the Mac's Terminal)

```sh
# Weekly content draft (2-round fix loop, idempotent per day):
launchctl kickstart -k gui/$(id -u)/ai.tmc.weekly_content
# Daily brief:
launchctl kickstart -k gui/$(id -u)/ai.tmc.daily_brief
# Verify an agent is registered:
launchctl print gui/$(id -u)/ai.tmc.weekly_content | head
```

If `ai.tmc.weekly_content` is not registered (e.g. after a `bootout`), bootstrap it (see §7).

---

## 5. Publish (branch → CI → preview → prod)

```sh
git checkout -b feat/<change>
# ...Codex edits...
python3 tools/tmc_ops.py verify-all && python3 tools/workspace_validate.py && python3 tools/workspace_build.py --check
git -c user.name="Mickey Wei" -c user.email="mickeyweijiajun@gmail.com" commit -am "<msg>"
git push -u origin feat/<change>        # (github credentials)
gh pr create --title "<t>" --body "<b>" # PR creation is allowed to be automatic
# CI runs verify-all + workspace gates; CF publishes a pr-N preview.
# Smoke the preview URL, then:
gh pr merge <n> --squash --delete-branch # deploys Production on main
```

Manual Cloudflare preview (bypassing PR) if needed:
```sh
pip install blake3
python3 tools/pages_deploy.py --branch <b>   # uses custom-cred:api.cloudflare.com
```

---

## 6. Rollback (Production regression)

```sh
# Fast path: revert the offending merge on main and re-push.
git revert <bad_commit> && git push
# Or restore the last-known-good snapshot:
git checkout final/perplexity-handoff-20260713   # @ efb9a9c
```
Cloudflare redeploys automatically on the next `main` push. Bad data → publish `DATA_UNAVAILABLE`,
never guess.

---

## 7. Known OWNER_ACTION — launchd bootstrap (Test 7)

`launchctl bootstrap` cannot run from a non-interactive session (launchd `gui/501` domain, `error 5`).
Run this in the Mac's own Terminal (or just log out/in — the valid plist auto-loads):
```sh
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.tmc.weekly_content.plist
```

---

## 8. Health & monitoring

- **Automated:** GitHub Actions `weekly-health.yml`, Mondays 09:30 Beijing (01:30 UTC), opens an issue
  only on change (notify-on-change). Fail-open by design.
- **On demand:** `python3 tools/weekly_health.py` → `STATUS: OK`.

---

## 9. Guardrails (always)

- WATCHLIST_ONLY. No trade/position/entry/stop/return/personalized fields in any content.
- Do not modify frozen assets (5 Skill Minis, main products, payment links) unless a real production fault.
- Never output/commit secrets, cookies, positions, cost-basis, banking, or paid ZIPs.
- Max 2 fix rounds / 2 retries, then mark BLOCKED and continue other work.
- Preview never writes Production; archive refuses SAMPLE; RSS GUID is week-unique.

---

## 10. Where things live

| Thing | Path |
|---|---|
| Site repo | `tmc-v3/website/tmc-site/` |
| Tools | `tools/{tmc_ops,build_site_data,publish_brief_page,pages_deploy,weekly_health,backfill_radar_meta,workspace_validate,workspace_build}.py` |
| CI / deploy / health workflows | `.github/workflows/{ci,deploy,weekly-health}.yml` |
| Data (single source) | `site/data/{radar-latest,radar-2026-W29,site-config}.json`, `site/data/workspace/*.json` |
| Schemas | `schemas/workspace/asset.schema.json` |
| Handoff docs | `docs/handoff/*.md` |
| Protocol / rollback | `docs/{DUAL_ENGINE_PROTOCOL,ROLLBACK,TAKEOVER_MATRIX}.md` |
| Mac production | `/Users/mikicourage/TradingMapClaw/ops_migration/` |
