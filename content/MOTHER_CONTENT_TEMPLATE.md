<!-- status: DRAFT — requires Mickey approval before publishing -->
# Mother Content Template — "Weekly Market Intelligence Brief"

**Purpose:** one weekly "mother" piece, written once, that seeds all channel-specific derivatives for the week (see `REPURPOSE_FLOW.md`). Written every Monday. All numbers/claims must trace to `FACTS.md` (current version noted in the header below); all data points carry an as-of date and a source.

**Compliance red lines (from FACTS.md §5 — always apply, no exceptions):**
1. Scenario labels only — bullish / neutral / bearish. Never buy/sell/hold, never "signal," never "pick."
2. No promised returns. No "guaranteed," "can't lose," "beat the market."
3. No fabricated real-time data. Every figure carries an as-of date; missing data is written as `DATA_UNAVAILABLE`, never guessed.
4. No disclosure of Mickey's personal positions, orders, accounts, or dollar amounts.
5. "High conviction" → write "high research priority" or "high evidence density" instead.
6. Every piece carries: *"Research & education only. Not investment advice. · WATCHLIST_ONLY"*
7. Chinese-language public copy never writes "cron" — use "定时任务."
8. Default status is DRAFT. Nothing ships to any channel without Mickey's explicit approval.
9. No fabricated customers, earnings, or testimonials — ever.

---

## Template Structure

```markdown
# Weekly Market Intelligence Brief — Week of {YYYY-MM-DD}

**FACTS.md version referenced:** v{X.X.X}, as-of {YYYY-MM-DD}
**Status:** DRAFT — requires Mickey approval before publishing
**Compliance check:** scenario-label-only ✅ / no fabricated data ✅ / as-of dates present ✅

## This Week's Theme
(1 sentence: the throughline connecting the 3 observations below — a market
structure question, a research-method angle, or a build-log milestone. Not a
prediction. Framed as a research question the week's cycle explored.)

## Key Observation 1
**As-of:** {YYYY-MM-DD}
**Source(s):** {data source name + link/citation}
- What the dual-engine cycle found (Pass A/B/C summary as relevant)
- Scenario label: bullish / neutral / bearish (with the "why," not a call to action)
- If Engine 1 and Engine 2 disagreed on this observation, say so explicitly

## Key Observation 2
**As-of:** {YYYY-MM-DD}
**Source(s):** {data source name + link/citation}
(same structure as Observation 1)

## Key Observation 3
**As-of:** {YYYY-MM-DD}
**Source(s):** {data source name + link/citation}
(same structure as Observation 1)

## Engine Disagreement Spotlight
One concrete example this cycle where Engine 1 (Hermes Agent) and Engine 2
(Codex) produced different reads before council resolution. Show the
disagreement, the tiebreaker path if used (DeepSeek → GLM-5.2 → GPT-5.6), and
the final blended scenario label. If no disagreement occurred this cycle,
state that explicitly rather than omitting the section.

## Method Corner
One rotating method note (S-Factor scoring / cross-verification practice /
supply-chain mapping / another research technique). Method only — never
tied to a specific outcome or performance claim.

## What I'm Watching Next Week
1–2 sentences: research questions the system will run next, framed as
open questions, not predictions of direction.

## Compliance Footer (required, verbatim)
*Research & education only. Not investment advice. · WATCHLIST_ONLY.
Scenario labels (bullish/neutral/bearish) only — never a buy/sell call, never
a signal, never a guarantee. Sample data is explicitly labeled as sample;
nothing here is described as live unless it is. Full disclaimer:
https://www.tradingmapclaw.com/legal/disclaimer*
```

---

## Notes for the Writer (Mickey or delegated drafter)

- Pull the FACTS.md version number into the header every week — if FACTS.md has been revised since the last brief, note what changed in one line before the theme section.
- "Key Observation" is not a euphemism for a stock pick. It should read like a research finding a bank ops analyst would write in an internal note — specific, sourced, dated, hedged where appropriate.
- The Engine Disagreement Spotlight is the single most differentiating section of this template — do not skip it or replace it with a generic "system update." If no disagreement occurred, say that plainly (it is itself informative).
- Every derivative in `REPURPOSE_FLOW.md` traces back to this document as its `source` field in `FOUR_WEEK_SCHEDULE.csv`. If the mother brief is not marked READY, no derivative built from it can be marked READY either.
