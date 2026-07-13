<!-- status: DRAFT — requires Mickey approval before publishing -->
# X / Twitter Content — TradingMapClaw Launch Kit
**Status: DRAFT — not for posting until Mickey approves.**

Voice: first-person, Mickey Wei. Financial-grade, confident, specific, honest. Story-driven but factual. Scenario labels only (bullish/neutral/bearish) — never "signals," "picks," "buy/sell," "guaranteed," "beat the market." Every post ends toward tradingmapclaw.com or the Substack.

All numbers below are locked to FACTS.md (2026-07-12, v2.0): 118 scheduled workflows (117 enabled) · 230+ Python scripts · 50+ skills · 82 tracked assets in 5 groups · 13 report types · 12+ data sources · ~$55/month budget cap (actual ~$7/mo) · v2.0 · built solo since May 2026 on one Mac mini.

---

## 1. Pinned Story Post

I have one working hand. Eight surgeries. A permanent ostomy. Zero coding background before May 2026.

Two months later I'd built a dual-engine AI research system that tracks 82 assets across 5 groups, cross-checks its own numbers, and runs for about $7/month against a $55 budget cap.

It doesn't know who built it. That's the point.

This is TradingMapClaw — research & education only, never investment advice. Story, system, and how to follow along: https://www.tradingmapclaw.com/story

Not pity. Visibility.

---

## 2. Launch Thread (8–12 tweets)

**Tweet 1/10**
I have one working hand. Eight surgeries. A permanent ostomy. Wells Fargo, Deutsche Bank, UBS, JPMorgan, eToro — back-office operations, not trading. Zero coding background before May 2026.

Here's what I built since, and why it matters more than my story does. 🧵

**Tweet 2/10**
Back-office isn't the trading floor. It's settlement, reconciliation, maker-checker — the machinery that makes sure a number is right before anyone acts on it.

That discipline is the actual foundation of what I built. Not the code. The checking.

**Tweet 3/10**
In May 2026 I started building a research system for myself: something to track markets I care about without paying for six different terminals.

I had never written a line of production code. AI was my engineering partner — I described intent, reviewed every line, tested, shipped.

**Tweet 4/10**
Two months later: TradingMapClaw. 118 scheduled workflows (117 enabled), 230+ Python scripts, 50+ skills, 82 tracked assets across 5 groups, 12+ data sources. Runs on one Mac mini. Budget cap ~$55/month — actual spend is closer to $7/month.

**Tweet 5/10**
The core idea, carried over from bank operations: never trust a single number. So the system runs a dual-engine architecture.

Engine 1 (Hermes Agent) orchestrates fundamentals, valuation, insider activity, and macro/industry/sentiment passes.

**Tweet 6/10**
Engine 2 (Codex) works independently — technicals, capital flow, options — and its mandatory job is to cross-verify Engine 1's numbers before anything ships. Four-eyes review, but for research output instead of trade settlement.

**Tweet 7/10**
Above both engines sits a Multi-Model Council: DeepSeek V4 Pro, GLM-5.2, GPT-5.6, with a local Qwen3 14B as fallback. When the council disagrees, there's a defined tiebreaker order — DeepSeek → GLM-5.2 → GPT-5.6.

**Tweet 8/10**
Every research cycle runs three analysis passes: Pass A fundamentals (40%, Engine 1), Pass B technicals + cross-verification (35%, Engine 2), Pass C macro/sentiment (25%, Engine 1). 13 report types come out the other end.

**Tweet 9/10**
None of this produces buy/sell calls. Output is scenario labels only — bullish / neutral / bearish — because that's what research is for. This is research & education, not investment advice, not a brokerage, not auto-trading.

**Tweet 10/10**
It doesn't know it was built by a man with one hand and a stoma bag. It just runs. That's the whole point of the story — ability first, background second.

Weekly Market Radar, build logs, and the products behind this system: https://www.tradingmapclaw.com

Not pity. Visibility.

---

## 3. Follow-up Short Posts (6)

**Short post 1**
118 scheduled workflows. 117 of them enabled and running right now. One Mac mini. ~$7/month actual spend against a $55 cap. This is what a solo-built research operating system looks like from the inside. https://www.tradingmapclaw.com

**Short post 2**
The hardest engineering lesson I brought from bank back-office work into AI research: a single unverified number can cascade into a failure nobody catches until it's expensive. That's why nothing in this system ships without a second engine checking it.

**Short post 3**
82 tracked assets across 5 groups. 13 report types. 12+ data sources feeding in. All of it research and education — scenario labels only, never a pick, never a signal. Weekly Market Radar is free: https://www.tradingmapclaw.com/radar

**Short post 4**
Zero coding background before May 2026. That's not a humble-brag — it's the actual starting condition. AI can be a real engineering partner if you bring the discipline to review every line yourself. More on how, in the System Build Log.

**Short post 5**
A council of three AI models — DeepSeek V4 Pro, GLM-5.2, GPT-5.6 — with a defined tiebreaker order when they disagree. One model can be confidently wrong. A council makes disagreement visible instead of hidden.

**Short post 6**
This system will never tell you to buy or sell anything. It outputs bullish / neutral / bearish scenario labels because that's honest about what research can and can't tell you. Full disclaimer and method: https://www.tradingmapclaw.com/faq

---

## 4. Technical Architecture Posts (3)

**Technical post 1 — The dual engine**
Most "AI trading" content is one model talking to itself. TradingMapClaw runs two independent engines instead.

Engine 1 (Hermes Agent) orchestrates and produces the first pass: fundamentals, valuation, insider activity, macro/industry/sentiment.

Engine 2 (Codex) is not a second opinion for style — it's a mandatory checker. It independently runs technicals, capital flow, and options analysis, and its job includes cross-verifying Engine 1's numbers before output ships.

This mirrors maker-checker controls from bank operations, not a trading strategy. Detail: https://www.tradingmapclaw.com/deep-analysis

**Technical post 2 — The council and the passes**
Above the two engines sits a Multi-Model Council: DeepSeek V4 Pro, GLM-5.2, GPT-5.6, plus a local Qwen3 14B closing the fallback chain. When the council disagrees, there's a fixed tiebreaker: DeepSeek → GLM-5.2 → GPT-5.6.

Every research cycle runs three weighted passes — Pass A fundamentals (40%, Engine 1), Pass B technicals + cross-verification (35%, Engine 2), Pass C macro/sentiment (25%, Engine 1) — never described as "three engines," because the engine count is two; the passes are the analysis structure. More: https://www.tradingmapclaw.com/deep-analysis

**Technical post 3 — The infrastructure**
Under the hood: 118 scheduled workflows (117 enabled), 230+ Python scripts, 50+ skills, 12+ data sources, one Mac mini, ~$7/month actual spend against a $55 budget cap. No cloud cluster, no team — one person's operating discipline applied to AI-assisted engineering.

I go layer by layer in the System Build Log on the Substack: https://tradingmapclaw.substack.com

---

## 5. Market-Research-Method Posts (3)
Describe method only. Never picks, never tickers, never outcomes.

**Method post 1 — S-Factor**
Part of how the system scores an asset for research purposes is what I call the S-Factor: a structured way of weighting qualitative signal strength (sentiment, narrative, positioning) against quantitative fundamentals, instead of letting either dominate. It's a scoring method, not a prediction — the output is a scenario label, not a call. Method notes: https://www.tradingmapclaw.com/deep-analysis

**Method post 2 — Cross-verification**
The single most defensible piece of this system isn't any one model — it's that Engine 2 is required to independently re-derive Engine 1's key numbers before a report ships. If the two engines disagree, that disagreement is surfaced, not smoothed over. This is a research-integrity method borrowed directly from bank maker-checker controls, applied to AI output instead of trade settlement.

**Method post 3 — Supply-chain mapping**
One research method the system runs: mapping a company's supply chain outward — suppliers, customers, dependencies — to understand exposure that a single-company fundamentals view misses. It's a structural research technique, not a forecasting tool, and it feeds into the macro/industry pass (Pass C) alongside sentiment. Research & education only: https://www.tradingmapclaw.com/faq

---

*All content above is DRAFT pending Mickey's review and approval before posting. No fabricated metrics, customers, testimonials, or returns are included. CTAs point to tradingmapclaw.com or the Substack only.*
