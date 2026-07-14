# Handoff — Start Here (Perplexity exit entry point)

If Perplexity is gone, this folder is your operating manual. Read in this order:

1. **[OPERATIONS_AFTER_PERPLEXITY.md](OPERATIONS_AFTER_PERPLEXITY.md)** — how to run the system with only
   Hermes (Mac) + Codex (GitHub/Cloudflare) + GitHub Actions. Start here to *do* anything.
2. **[FINAL_HANDOFF_20260714.md](FINAL_HANDOFF_20260714.md)** — the authoritative record: P0/P1/P2 results,
   Mac SHA + Test 6/7, ownership, LaunchAgents, Workspace evidence, commit/CI/Preview/Prod/rollback,
   degradation, OWNER_ACTION, BLOCKED reasons, shortest continue-commands.
3. **[SYSTEM_OWNERSHIP_MATRIX.md](SYSTEM_OWNERSHIP_MATRIX.md)** — who owns which task, and the rules.
4. **[FINAL_ACCEPTANCE_TESTS.md](FINAL_ACCEPTANCE_TESTS.md)** — every acceptance test with re-run commands.

Related authoritative docs: `../DUAL_ENGINE_PROTOCOL.md`, `../ROLLBACK.md`, `../TAKEOVER_MATRIX.md`.

---

## 30-second start

```sh
cd tmc-v3/website/tmc-site
# 1) verify the site is healthy (Codex, deterministic, no LLM):
python3 tools/tmc_ops.py verify-all && python3 tools/workspace_validate.py && python3 tools/workspace_build.py --check
# 2) trigger content (Hermes, on the Mac's own Terminal):
launchctl kickstart -k gui/$(id -u)/ai.tmc.weekly_content
# 3) publish: branch → PR → CI gate → CF preview → smoke → merge main
```

## The one human step you may still need

Run once in the Mac's own Terminal to re-register the weekly-content agent (launchd gui-domain limit):
```sh
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.tmc.weekly_content.plist
```

## Non-negotiables

- WATCHLIST_ONLY · research & education only · not investment advice.
- Don't touch trading/broker/execution, `memory.sqlite`, scheduler, `stocks.yaml`, or the frozen
  Payhip products/links — unless there's a real production fault (then: backup + rollback first).
- Preview never writes Production. LIVE requires dual-PASS + FRESH. Bad data → `DATA_UNAVAILABLE`.
