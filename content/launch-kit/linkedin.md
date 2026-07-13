<!-- status: DRAFT — requires Mickey approval before publishing -->
# LinkedIn Content — TradingMapClaw Launch Kit
**Status: DRAFT — not for posting until Mickey approves.**

Voice: first-person, Mickey Wei. Financial-grade, confident, specific, honest, story-driven but factual. Scenario labels only. Every piece ends toward tradingmapclaw.com or the Substack.

---

## 1. Personal "About" Section

I have one working hand, eight surgeries behind me, and a permanent ostomy. I spent my career in back-office operations at Wells Fargo, Deutsche Bank, UBS, JPMorgan, and eToro — settlement, reconciliation, maker-checker controls. Not the trading floor. The machinery that makes sure a number is right before anyone acts on it.

In May 2026, with zero coding background, I started building a research system for myself. Two months later it became TradingMapClaw — an independent AI-powered market intelligence and research operating system, built solo on one Mac mini, running on roughly $7 a month against a $55 budget cap.

The system runs a dual-engine architecture: Engine 1 (Hermes Agent) orchestrates fundamentals, valuation, insider, and macro/sentiment analysis; Engine 2 (Codex) independently checks technicals, capital flow, and options — and is required to cross-verify Engine 1's numbers before anything ships. Above both sits a Multi-Model Council: DeepSeek V4 Pro, GLM-5.2, and GPT-5.6.

Everything it outputs is research and education. Scenario labels only — bullish, neutral, bearish. Never a pick, never a signal, never advice.

I write about both halves of this in public: the engineering, and the life that shaped how I think about verification, risk, and building things that don't fail quietly.

Not pity. Visibility.

More: https://www.tradingmapclaw.com/story · https://tradingmapclaw.substack.com

---

## 2. Project Intro (for Featured section / project post)

**TradingMapClaw — Dual-Engine AI Research Operating System**

TradingMapClaw is an independent AI-powered market intelligence and research system I built solo, starting from zero coding background in May 2026. It now runs 118 scheduled workflows (117 enabled), 230+ Python scripts, and 50+ skills, tracking 82 assets across 5 groups, producing 13 report types from 12+ data sources — all on one Mac mini for roughly $7/month against a $55 budget cap.

The architecture is deliberately built around verification, not speed: two independent AI engines (Hermes Agent and Codex) cross-check each other's numbers, coordinated by a council of three models (DeepSeek V4 Pro, GLM-5.2, GPT-5.6) with a defined tiebreaker order when they disagree.

Output is research and education only — bullish/neutral/bearish scenario labels, never investment advice, never a trade signal.

Free intelligence (Weekly Market Radar, Engine Disagreement Brief, System Build Log) and paid tutorials on how the system itself was built are both available at https://www.tradingmapclaw.com.

---

## 3. Launch Long-Form Article (~800 words)

**Title: The System Doesn't Know It Was Built With One Hand**

Eight surgeries. One working hand. A permanent ostomy. Those are facts about my body, not qualifications, and for most of my career I kept them out of the room entirely.

I spent years in back-office operations at Wells Fargo, Deutsche Bank, UBS, JPMorgan, and eToro. Not the trading floor — the machinery underneath it. Settlement. Reconciliation. Maker-checker controls. The unglamorous discipline that exists because a single unverified number, left unchecked, can cascade into a failure nobody catches until it's expensive. That discipline turned out to be the most valuable thing I carried out of banking, and I didn't know it at the time.

In May 2026 I decided to build something for myself: a research system that could track the markets I follow, without paying for six different terminals and without trusting any single source blindly. I had zero coding background. What I had was AI as an engineering partner, and the operational instincts from years of maker-checker review.

Two months later, that system exists. I call it TradingMapClaw.

**What it actually is**

TradingMapClaw is an independent AI-powered market intelligence and research operating system — not a signal service, not a robo-advisor, not a brokerage. It runs 118 scheduled workflows, 117 of them enabled right now, executing 230+ Python scripts and 50+ skills across 82 tracked assets in 5 groups, pulling from 12+ data sources, and producing 13 distinct report types. It runs entirely on one Mac mini. Actual monthly spend is around $7, against a self-imposed budget cap of $55.

None of that matters if the output can't be trusted. So the architecture is built around a principle I learned watching trades settle: never let one party mark their own homework.

**The dual engine**

Engine 1, which I call Hermes Agent, is the orchestrator. It runs fundamentals, valuation, insider-activity, and macro/industry/sentiment analysis. Engine 2, Codex, works independently — technicals, capital flow, options — and carries a mandatory responsibility: cross-verify Engine 1's numbers before any report ships. If the two disagree, that disagreement is surfaced, not smoothed away.

Above both engines sits a Multi-Model Council — DeepSeek V4 Pro, GLM-5.2, and GPT-5.6, with a local Qwen3 14B closing out the fallback chain if something upstream fails. When the council can't reach consensus, there's a defined tiebreaker order: DeepSeek → GLM-5.2 → GPT-5.6. One model can be confidently wrong. A council makes that visible instead of hidden.

Every research cycle runs three weighted analysis passes: Pass A, fundamentals, weighted 40% and run by Engine 1; Pass B, technicals plus cross-verification, weighted 35% and run by Engine 2; Pass C, macro and sentiment, weighted 25% and run by Engine 1. I'm careful never to call this "three engines" — there are two engines and three analysis passes, and conflating them would misdescribe how the system actually works.

**What it will never do**

TradingMapClaw is research and education only. It is not investment advice, not personalized advice, not a brokerage, not fund management, not trade execution, not auto-trading, not copy-trading. Every output is a scenario label — bullish, neutral, or bearish — never a buy/sell call, never a "signal," never a "pick," never a guarantee. I built it watchlist-only on purpose, and I'm keeping it that way.

**Why I'm writing this down publicly**

I'm not sharing my background for sympathy. People living with what I live with — nerve injury, permanent ostomies, the daily logistics that come with them — tend to be invisible in professional spaces, not because it's rare, but because the people it happens to tend to go quiet. I'd rather be specific and visible than quiet and comfortable.

The system doesn't know or care who built it. It just runs — every scheduled workflow, every cross-check, every report — regardless of how many hands typed the code that built it. That indifference is the whole point. Ability first, background second.

If you want to follow the build in detail — the free Weekly Market Radar, the Engine Disagreement Brief, and the System Build Log — everything is at https://www.tradingmapclaw.com and https://tradingmapclaw.substack.com. If you want to understand how the system was actually built, the tutorial series walks through it layer by layer, starting at https://www.tradingmapclaw.com/products.

Not pity. Visibility.

---

## 4. Follow-up Article Drafts (~400 words each)

### Article 2: "Why Two AI Engines Instead of One"

Most people building with AI today use one model and trust its output. I built TradingMapClaw around a different assumption: one model, however capable, can be confidently wrong — and confidence is not the same as correctness.

That assumption came directly from bank back-office work. In settlement and reconciliation, nothing runs on trust alone. Every number needs an audit trail. Every trade needs a checker independent of the person who made it. A maker proposes; a checker verifies; only then does it move forward. I spent years inside that discipline at Wells Fargo, Deutsche Bank, UBS, and JPMorgan, and it shaped how I think about any system that produces numbers people might rely on.

So when I designed TradingMapClaw's research architecture, I didn't build one AI pipeline. I built two independent engines. Engine 1, Hermes Agent, orchestrates the first pass — fundamentals, valuation, insider activity, macro and sentiment context. Engine 2, Codex, works independently on technicals, capital flow, and options, and carries a specific mandatory job: cross-verify Engine 1's numbers before anything is published. It is not a stylistic second opinion. It's a checker.

Above both engines is a Multi-Model Council — DeepSeek V4 Pro, GLM-5.2, and GPT-5.6, with a local Qwen3 14B as the fallback of last resort. When the council disagrees, there's a fixed resolution order rather than an arbitrary pick. Disagreement gets a name and a path, not a shrug.

The result isn't a system that's always right — no research system is. It's a system where you can see when the two engines disagree, instead of only ever seeing one confident answer with no way to check it. I think that visibility is more valuable than false certainty, and it's the single most defensible design decision in the whole project.

This is still research and education, not investment advice — every output lands as a bullish/neutral/bearish scenario label, never a pick. But the mechanism behind the label is, I'd argue, more honest than most single-model tools claim to be.

More on the architecture: https://www.tradingmapclaw.com/deep-analysis. Weekly build notes on the Substack: https://tradingmapclaw.substack.com.

---

### Article 3: "What $7 a Month Actually Buys"

I set a budget cap of $55 a month when I started building TradingMapClaw. Actual spend has run closer to $7 a month. I want to explain why that gap exists, because I think it says something useful about building AI systems solo.

The $55 cap was a discipline device, not a target — a ceiling I set for myself so cost could never quietly become the reason the project stalled. What actually happened is that a well-designed scheduling and caching architecture, running on hardware I already owned, needed far less than the ceiling allowed.

The system runs 118 scheduled workflows, 117 of them currently enabled, executing 230+ Python scripts and 50+ skills. It pulls from 12+ data sources and produces 13 report types across 82 tracked assets in 5 groups. All of that runs on one Mac mini I already had — no cloud cluster, no dedicated GPU rental, no team.

Cost control here isn't a trick; it's a byproduct of an architecture built for verification over volume. Two engines cross-checking each other's numbers, rather than one model producing endless speculative output, means fewer wasted calls. A defined model fallback chain — DeepSeek V4 Pro, GLM-5.2, GPT-5.6, and a local Qwen3 14B as backstop — means the system degrades gracefully instead of failing expensively when one provider has an outage.

I mention the real number, not just the cap, because I think most "built cheap" claims in this space understate what's actually being spent, or overstate what a hobby project can do. I'd rather be specific: the budget is $55, the actual bill is about $7, and the difference is architecture, not magic.

None of this is investment advice — it's an engineering note about running a solo research system efficiently. Full build log: https://tradingmapclaw.substack.com. System overview: https://www.tradingmapclaw.com.

---

### Article 4: "Research and Education, Not Advice — Why the Line Matters to Me"

Every report TradingMapClaw produces ends in one of three words: bullish, neutral, or bearish. Never buy. Never sell. Never a target price framed as a promise. That's not a legal disclaimer bolted onto marketing copy — it's a line I drew deliberately, and I want to explain why I care about it as much as I do.

I spent years in bank back-office operations — settlement, reconciliation, KYC, maker-checker controls — watching how much infrastructure exists specifically to prevent a single unverified claim from causing real financial harm. That experience left me with a strong distaste for confident-sounding output that hasn't earned its confidence.

TradingMapClaw is research and education only. It is not investment advice, not personalized advice, not a brokerage, not fund management, and it does not execute trades, auto-trade, or copy-trade. Every output is a scenario label — bullish, neutral, or bearish — describing what the dual-engine analysis found, not what to do about it. The Weekly Market Radar sample data is refreshed weekly and labeled as such; I never describe anything as "live" when it isn't.

I think this distinction gets blurred constantly in AI-and-markets content, usually because "signals" and "picks" sell better than honest scenario labels. I'd rather build something slower to monetize and durable to trust than something that grows fast and eventually needs a correction nobody wants to issue.

If you want a system that helps you think more rigorously about markets — without pretending to think for you — that's what I built. Everything here, including the disclaimer language itself, is public: https://www.tradingmapclaw.com/disclaimer and https://www.tradingmapclaw.com/faq. Free weekly research: https://tradingmapclaw.substack.com.

---

*All content above is DRAFT pending Mickey's review and approval before posting. No fabricated metrics, customers, testimonials, or returns are included. CTAs point to tradingmapclaw.com or the Substack only.*
