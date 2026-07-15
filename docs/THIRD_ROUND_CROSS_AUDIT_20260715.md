# Third-round cross-audit — public repository findings

Date: 2026-07-15. Scope: `TradingMapClaw` documentation repo, `tradingmapclaw-website`, and the supplied Hermes Round 2 report. Mac-only code under `~/.hermes/` was not mounted in this review environment and is therefore not marked independently verified.

## Confirmed

- Both public GitHub repositories are accessible with push/admin permission through the connected GitHub identity.
- Website repository history and the stated main commit were located.
- Website unit suite passed before changes (8 tests).
- Existing local quality gate passed before changes (25 PASS, 0 FAIL, 0 WARN, 3 network SKIP).
- Existing public workspace contained ten asset records, only NVDA LIVE and the others safe `UNAVAILABLE` tombstones.

## Material findings

1. **The candidate checker was overstated.** It validated producer-supplied JSON and source values but did not retrieve the external sources. It is now described as deterministic preflight and reports `external_fact_check=NOT_PERFORMED`.
2. **Freshness was producer-controlled.** The checker trusted `freshness.state=FRESH`. It now recomputes age from `data_as_of`; LIVE records must be within `max_age_days`.
3. **LIVE source diversity was not enforced.** LIVE now requires at least two distinct source domains.
4. **The Hermes report contains an internal cron-count contradiction.** It reports both 118/121 and later corrects 118 OK to 117 OK + 2 errors + 2 disabled. No public canon should change until a Mac-generated snapshot resolves this.
5. **Engine terminology drift remains in the audit report.** The system is two engines running three passes with a multi-model council—not three independent engines.
6. **Council default risk.** Changing `call_hermes()`'s default to DeepSeek can affect unrelated callers. Round model/provider pairs should be explicit at each call site; the function default should be neutral/config-driven.
7. **Browser automation evidence is incomplete.** The excerpted temp-file approach needs `try/finally` cleanup and should remain disabled until a real logged run succeeds.
8. **PAT evidence was not transferable.** Hermes proved its own token could push. The connected Codex identity can write both public repos, but the private `tmc-shared-context` repo was not visible in this environment.
9. **Public AI-agent text exposed unsafe internal wording.** `llms-full.txt` used real-time, position, options-strategy and next-session recommendation language. It was rewritten as scheduled, watchlist-only research context.
10. **Public facts are drifting.** The supplied current Mac inventory says 415+ scripts while public canon says 230+. A reproducible Mac snapshot is required before changing marketing numbers.

Public-facing scale wording has therefore been changed to `100+ scheduled workflows` and `hundreds of scripts`; exact counts remain internal and pending snapshot reconciliation.

## Changes in this iteration

- Added schemas and deterministic writer for public system updates and Verification Ledgers.
- Added fixed-cadence, zero-additional-token Mac outbox publishing design.
- Added an auditable public Verification Ledger page and machine-readable feed.
- Added a machine-readable Build Log feed and website rendering.
- Expanded legal publication/verification disclosures.
- Tightened workspace freshness/source checks and public-feed CI checks.
- Added a Mac launchd design: system updates may auto-merge after CI; research ledgers stop at a reviewable PR.

## Mac evidence still required

- `.env` model-variable precedence and key presence (values redacted).
- Complete `config.yaml` fallback chain.
- `codex_council.py` prompts, explicit model assignment, error fallback, vote parsing and conditional R3 behavior.
- `zhipu_autobuy.py` cleanup and one successful logged browser run.
- Active `.py` scan for stale model identifiers across both script roots.
- Exported cron snapshot with unique job IDs and current status counts.
- `task_queue.json` state and the private bridge repository visibility.

These are verified by the companion Mac snapshot script in the documentation repository; until that output is attached, Hermes's six Mac fixes remain **reported, not independently confirmed**.
