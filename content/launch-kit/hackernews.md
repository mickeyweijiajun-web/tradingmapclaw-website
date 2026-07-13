<!-- status: DRAFT — requires Mickey approval before publishing -->
# Hacker News Content — TradingMapClaw Launch Kit
**Status: DRAFT — not for posting until Mickey approves.**

Note: HN's audience is skeptical of AI-and-finance claims by default and will stress-test every number. Only post facts from FACTS.md. Do not editorialize about returns, performance, or picks anywhere in this thread — HN will call it out immediately if it drifts toward advice framing.

---

## Show HN Title

Show HN: I built a dual-engine AI research system solo, with one working hand, for $7/month

*(Alternate, more architecture-forward title if the above reads too personal for the front page: "Show HN: TradingMapClaw – two independent AI engines that cross-check each other's market research")*

---

## Show HN Body

Hi HN. I'm Mickey — back-office operations at a few global banks (Wells Fargo, Deutsche Bank, UBS, JPMorgan, eToro: settlement, reconciliation, maker-checker controls), not a trader, not previously an engineer. I have one working hand, have had eight surgeries, and live with a permanent ostomy. None of that is the pitch — it's context for why AI-assisted coding was the only realistic way I could build this myself, and why I leaned so heavily on verification patterns from bank operations when designing it.

**What it is:** TradingMapClaw is an independent AI-powered market research and intelligence system — not a signal service, not a robo-advisor, not a brokerage. Research and education only. It outputs bullish/neutral/bearish scenario labels, never buy/sell calls, never "picks."

**The architecture, briefly:**
- Two independent engines. Engine 1 (Hermes Agent) orchestrates fundamentals, valuation, insider activity, and macro/sentiment analysis. Engine 2 (Codex) independently runs technicals, capital flow, and options — and is required to cross-verify Engine 1's numbers before anything ships. This is a maker-checker pattern lifted directly from bank settlement operations, applied to AI research output instead of trade processing.
- A Multi-Model Council above both engines — DeepSeek V4 Pro, GLM-5.2, GPT-5.6 — with a local Qwen3 14B closing the fallback chain, and a fixed tiebreak order (DeepSeek → GLM-5.2 → GPT-5.6) when the council doesn't converge.
- Three weighted analysis passes per cycle: fundamentals (40%, Engine 1), technicals + cross-verification (35%, Engine 2), macro/sentiment (25%, Engine 1). I deliberately don't call this "three engines" anywhere — there are two engines and three analysis passes, and I try to be precise about the distinction.

**The numbers, as of today (v2.0, 2026-07-12):** 118 scheduled workflows (117 enabled), 230+ Python scripts, 50+ skills, 82 tracked assets across 5 groups, 13 report types, 12+ data sources. Runs on one Mac mini. Actual spend is around $7/month against a self-imposed $55/month cap.

Built solo since May 2026, starting from zero coding background. I describe intent to AI, review every line, test, and ship — the same discipline I'd apply reviewing a reconciliation break before signing off on it.

There's a free weekly research layer (Market Radar, an Engine Disagreement Brief, a build log) and paid tutorials on how the system itself was built. Everything, including the disclaimer language, is public at https://www.tradingmapclaw.com. Happy to answer anything — architecture, cost breakdown, the AI-assisted build process, or the disability angle if that's what you're curious about.

---

## Anticipated Q&A (8 questions, honest answers)

**1. Is this investment advice?**
No. TradingMapClaw is research and education only — not personalized advice, not a brokerage, not fund management, not trade execution, not auto-trading, not copy-trading. Every output is a scenario label (bullish/neutral/bearish), never a buy/sell call, never a "signal" or a "pick." The full disclaimer is public at tradingmapclaw.com/legal/disclaimer.

**2. Why two engines instead of one good model?**
Because one model, however capable, can be confidently wrong, and confidence isn't correctness. I came from bank operations where nothing ships without an independent checker — a maker proposes, a checker verifies. Engine 2 (Codex) is required to cross-verify Engine 1's (Hermes Agent's) numbers before a report goes out. If they disagree, that's surfaced rather than silently resolved. It's a verification pattern, not a performance claim.

**3. How is $55/month (or $7/month) actually possible for this much infrastructure?**
Honestly: it runs on hardware I already own (one Mac mini), so there's no cloud compute or hosting bill beyond API usage. The scheduling and caching architecture is designed to minimize redundant model calls — two engines that specialize and cross-check, rather than one model called repeatedly for everything, actually uses fewer tokens than it sounds like. The $55 is a self-imposed ceiling, a discipline device more than a real constraint; actual spend has run closer to $7/month on API costs. I'm not hiding a bigger bill somewhere — this is a personal-scale project, not enterprise infrastructure.

**4. What happens if all three council models disagree or go down?**
There's a defined tiebreaker order (DeepSeek V4 Pro → GLM-5.2 → GPT-5.6) for disagreement, and a local Qwen3 14B model closes out the fallback chain if the cloud models are unavailable. The system is built to degrade gracefully rather than fail silently or produce output with hidden gaps.

**5. Are you backtesting this or claiming any performance numbers?**
No performance, return, or win-rate numbers are published, because none have been rigorously verified to a standard I'd stand behind, and I won't publish a number I can't defend under scrutiny. The Weekly Market Radar sample data refreshes weekly and is explicitly labeled as such — never described as "live." This is a research and education tool; performance marketing isn't part of what it does.

**6. Do the banks you worked at (Wells Fargo, Deutsche Bank, UBS, JPMorgan, eToro) endorse this?**
No. That's career history only, not an endorsement of any kind, and I'm careful never to imply otherwise. My time in those roles shaped the operational discipline behind the design — that's the entire connection.

**7. What's the actual tech stack — models, scheduling, data sources?**
The AI layer is the Multi-Model Council (DeepSeek V4 Pro, GLM-5.2, GPT-5.6, local Qwen3 14B fallback) orchestrated by the two engines described above. Scheduling runs 118 workflows (117 currently enabled) across 230+ Python scripts and 50+ skills, pulling from 12+ data sources into 13 report types, all on one Mac mini. I go deeper on the actual layer-by-layer build in the tutorial series and the System Build Log rather than in this thread, since it's a lot of ground to cover.

**8. Why release tutorials on how you built it instead of just selling the tool itself?**
Two reasons. First, I don't have a live recurring subscription for the tool itself yet — the Skills & Methods Library is founding-waitlist only until I'm confident the delivery mechanism is solid, and I'd rather under-promise than sell something not fully ready. Second, I think the build process itself — going from zero coding background to a 118-workflow system using AI as an engineering partner — is genuinely useful information for other people trying to do something similar, independent of whether they care about markets at all.

---

*All content above is DRAFT pending Mickey's review and approval before posting. No fabricated metrics, customers, testimonials, or returns are included. CTA points to tradingmapclaw.com only.*
