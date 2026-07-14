# System Ownership Matrix (post-Perplexity)

As-of 2026-07-14. Discipline: **only real run logs count as "owned."** Docs, un-run scripts, dry-runs,
drafts, and test fixtures never count as a completed takeover.

Owner values: `HERMES` · `CODEX` · `DUAL-ENGINE` · `GITHUB-ACTIONS` · `CLOUDFLARE` · `OWNER` · `NOT-IMPLEMENTED`.

Compliance: WATCHLIST_ONLY. Trading/order/broker/execution, `memory.sqlite`, scheduler, and `stocks.yaml`
are **out of scope** and unchanged.

---

## A. Responsibilities

| Owner | Owns | Does NOT own |
|---|---|---|
| **Hermes** (Mac launchd) | Low-cost draft generation (weekly content, daily brief), orchestration, first-pass narrative lint | Publishing, code review, deploy, payments |
| **Codex** (GitHub + local tools) | Code, deterministic verification, CI, Cloudflare deploy, rollback, independent fact/engineering check | Narrative authoring, credential ownership |
| **GitHub Actions** | `ci.yml` (verify-all + workspace gates), `weekly-health.yml` (health, notify-on-change) | Content generation |
| **Cloudflare Pages** | Hosting — Preview per PR (`pr-N.…pages.dev`), Production on `main` (`www.tradingmapclaw.com`) | Content decisions |
| **Owner (Mickey)** | Payments, refunds, 2FA, terms acceptance, banking, account ownership, launchd GUI bootstrap, Perplexity-task retention decisions | Day-to-day generation/verify/deploy (automated) |

---

## B. Workflow / task matrix

| # | Task | Owner (target) | Schedule | Last real run / evidence | Status | Rollback |
|---|---|---|---|---|---|---|
| 1 | Daily market brief | LOCAL-DUAL-ENGINE `ai.tmc.daily_brief` | Weekdays 08:00 Beijing | 2026-07-13, OK 10/10, 13/13 independently re-checked; `sent=False` | OWNER_ACTION (push not wired) | Keep Perplexity `9b9748d6` |
| 2 | Weekly content + Substack draft | LOCAL-DUAL-ENGINE `ai.tmc.weekly_content` | Mon 09:30 Beijing | 2026-07-14 Test 6 PASS (`DRAFT_2026-07-14_method-note.md`, 2 fix rounds) | OWNER_ACTION (bootstrap §9.1) | Restore `.v1.bak.20260714`; Perplexity `d87c574c` fallback |
| 3 | Weekly GitHub health check | GITHUB-ACTIONS `weekly-health.yml` | Mon 09:30 Beijing (01:30 UTC) | GitHub Actions run, STATUS OK | PASS (owned) | Disable workflow → re-enable Perplexity `5196e484` (now deleted) |
| 4 | Weekly Radar (report) | DUAL-ENGINE (Hermes narrative + Codex verify/build) | Weekly | 2026-W29 real run: dual-source 9/9 → LIVE JSON → Preview → CI → Prod → archive + RSS | PASS | `git revert` + re-push main; bad data → DATA_UNAVAILABLE |
| 5 | Site publish pipeline | CODEX (CI/CF) | On PR / on main | PR #1 (P0-E), PR #2 (P2) both merged, Prod green | PASS | Revert to `efb9a9c` |
| 6 | Workspace pages | DUAL-ENGINE (data → validate → build → publish) | On data change | NVDA LIVE; MSTR/BTC Coming soon | PASS | Revert commit; UNAVAILABLE fallback |
| 7 | Payments / delivery | OWNER + Payhip/PayPal | — | 5 Skill Minis $9 + main products LIVE (unchanged) | PASS (do not modify) | N/A (Owner-only) |

---

## C. Ownership rules

1. A task is "owned" by Hermes/Codex/GitHub only after a **real** logged run — never on the basis of a
   plan, fixture, dry-run, or doc.
2. Reports that conflict with Production **defer to the measured Production state**.
3. Any change: backup + rollback point first; Branch → CI → Preview **before** Production; a Production
   regression triggers immediate restore of last-known-good.
4. Max 2 fix rounds per problem; max 2 retries per tool/connector error, then mark BLOCKED and continue
   other work.
5. Never output/commit tokens, API keys, cookies, IBKR/positions/cost-basis, banking, or paid ZIPs.

---

## D. Do-not-touch (frozen)

- 5 Skill Minis ($9): `payhip.com/b/{2cyOU,dYDvB,aUuJy,SyeE2,Iqe8j}`.
- Main products: T01 `ldF9E`, T02 `PqYSt`, T03 `8pogv`, Complete $49 `rdjMT`, Patterns $79 `Biug2`.
- Trading/order/broker/execution modules, `memory.sqlite`, scheduler, `stocks.yaml`.

*Change only on a real production fault, with backup + rollback first.*
