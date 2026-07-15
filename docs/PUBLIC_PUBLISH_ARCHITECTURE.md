# Public publishing architecture v2.2

As of 2026-07-15. This document defines the bridge from the Mac research system to `tradingmapclaw.com`. It is an engineering and compliance control, not legal advice.

## Outcome

The website gets useful new material without exposing positions, secrets, personalized output or action-oriented market language. Publishing reuses reports that already exist; the publication stage itself makes no LLM call.

## What is distinctive enough to publish

1. **Verification Ledger (weekly):** what Hermes claimed, what Codex challenged, which evidence survived, and what remains open. This is the strongest differentiator because the disagreement trail is normally hidden by other research products.
2. **Evidence / Counter-Evidence Delta (weekly, folded into the ledger):** what changed in the evidence set since the prior issue. No target, entry, sizing or action language.
3. **System Build Log (only when changed):** failures, fixes, tests, cost-control improvements and rollback notes. This proves the system is maintained rather than merely marketed.
4. **Source-health and data-quality notes (weekly):** source availability, stale fields, disagreement counts and `DATA_UNAVAILABLE` outcomes. Process metrics only.
5. **Cost ledger (monthly):** model-routing and infrastructure cost at system level. Never mix cost marketing with performance claims.

Do not publish personal positions, cost basis, account data, order or execution information, security-specific action levels, target prices, stop levels, options structures, personalized answers, urgent timing language, or unverified model output.

## Two release lanes

| Lane | Input | Frequency | Token cost | Merge policy |
|---|---|---:|---:|---|
| System update | Deterministic test/audit record | Daily check; publish only on change | 0 additional LLM tokens | CI auto-merge allowed |
| Verification ledger | Approved public copy of existing research | Weekly, fixed cadence | 0 additional tokens at publish time | Reviewable PR; no auto-merge |

The weekly lane may consume tokens earlier when Hermes writes and Codex checks the underlying internal report. The public stage does not run another model. Unchanged claims should be referenced from the previous ledger rather than rechecked, reducing checker cost.

## Data path

```text
~/.hermes/cron/reports/                       internal, never published directly
        |
        v
allowlisted public copy -> normalize -> redact -> deterministic compliance gate
        |
        v
public_intake.py (zero-token revision summary or validated bridge contract)
        |
        v
~/TradingMapClaw/public-content/approved/
        |-- system-updates/*.json
        `-- verification-ledgers/*.json
        |
        v
public_outbox.py -> public_release.py -> unit tests -> verify-all -> workspace gate
        |
        v
Git branch -> pull request -> GitHub Actions -> Cloudflare Preview
        |                                      |
        | system log: optional auto-merge      | research: owner review
        v                                      v
main -> Cloudflare Pages -> immutable archive + latest feed
```

Failure is fail-closed for public research and fail-open for the internal system: no publication failure may stop market-data collection or internal report generation.

## Required states

- `SYSTEM_BUILD_LOG`: `APPROVED`; engineering-only; may auto-merge after CI.
- `VERIFICATION_LEDGER`: `APPROVED_CANDIDATE`; `verification.hermes=PASS`; `verification.codex=PASS`; data age no more than seven days; every item has at least two independent HTTPS source domains.
- A deterministic schema/compliance pass must carry `external_fact_check=NOT_PERFORMED` when no source was actually retrieved. It cannot by itself create a LIVE research record.

## Mac schedule

- Daily 10:30 local time: `ai.tmc.public_system_log` maps a materially changed repository revision to safe engineering categories, then checks the system-update outbox. Commits that change only the public release feeds are ignored, preventing a self-triggering log loop. Empty runs exit with zero token cost and no network write.
- Monday 11:00 local time: `ai.tmc.public_research_ledger` validates `~/shared_context/public_verification_ledger.json`, then creates a reviewable PR for one new ledger. It never parses arbitrary report prose and never auto-merges.

The fixed cadence avoids urgency marketing and prevents the website from becoming a near-real-time signal feed.

## Compliance language

Prefer: `observed`, `evidence`, `counter-evidence`, `research question`, `source disagreement`, `DATA_UNAVAILABLE`, `general and impersonal`, `as of`.

Block: `buy`, `sell`, `hold`, `entry`, `stop loss`, `take profit`, `price target`, `position size`, `you should`, `act now`, `before the market`, `high conviction`, guaranteed-return language, and personal-account references.

Disclosures are necessary but not sufficient. The architecture limits the substance, timing and data fields before disclosure text is considered.

## Monetization fit

The free layer should demonstrate the verification method. Paid products may teach the workflow, templates and engineering patterns. Consulting remains system architecture and process work only. Research pages and sponsored content stay separate; any material commercial relationship is disclosed at first mention.

## Operating commands

```bash
python tools/public_release.py build-log approved-update.json --apply
python tools/public_release.py verification-ledger approved-ledger.json --apply
python tools/tmc_ops.py verify-all --skip-network
python -m unittest discover -s tests -v
```

On the Mac, `public_outbox.py` owns branch, PR and optional safe auto-merge handling. It refuses a dirty website repository and processes at most one approved file per run.

The bridge contract is intentionally narrow: the dual-engine system must emit the complete public ledger JSON, already redacted, with both verification results and HTTPS source links. Missing, stale, one-domain, malformed, action-oriented or previously processed records are rejected before GitHub is called.
