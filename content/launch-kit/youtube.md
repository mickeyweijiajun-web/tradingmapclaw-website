<!-- status: DRAFT — requires Mickey approval before publishing -->
# YouTube Content — TradingMapClaw Launch Kit
**Status: DRAFT — not for posting until Mickey approves.**

Format note: first video is screen-recording + voiceover, no face on camera. Voice: first-person Mickey Wei, financial-grade, confident, honest, story-driven but factual. Scenario labels only. No fabricated metrics.

---

## 1. Channel Description

TradingMapClaw is an independent AI-powered market intelligence and research operating system, built solo since May 2026 by one person — me, Mickey Wei — starting from zero coding background. This channel walks through how the system actually works: a dual-engine architecture (Hermes Agent orchestrating, Codex independently cross-verifying) coordinated by a Multi-Model Council (DeepSeek V4 Pro, GLM-5.2, GPT-5.6), running 118 scheduled workflows and 230+ scripts on one Mac mini for roughly $7/month.

Everything here is research and education, not investment advice. Output is scenario labels only — bullish, neutral, bearish — never a pick, never a signal. If you want the free weekly intelligence layer or the tutorials on how the system was built, everything is at https://www.tradingmapclaw.com and https://tradingmapclaw.substack.com.

Not pity. Visibility.

---

## 2. First Video — System Walkthrough (screen-recording + voiceover, no face)

### Title
How I Built a Dual-Engine AI Research System Solo (Zero Coding Background, $7/Month) — Full Walkthrough

### Description

I built TradingMapClaw entirely solo, starting in May 2026 with zero coding background. This video is a screen-recording walkthrough of how the system actually works: the dual-engine architecture, the multi-model council, the scheduling layer, and what it actually outputs.

Timestamps and key facts:
- Dual-engine design: Engine 1 (Hermes Agent) orchestrates fundamentals, valuation, insider, and macro/sentiment analysis. Engine 2 (Codex) independently checks technicals, capital flow, and options, and cross-verifies Engine 1's numbers.
- Multi-Model Council: DeepSeek V4 Pro, GLM-5.2, GPT-5.6, with local Qwen3 14B as fallback.
- Scale as of v2.0 (2026-07-12): 118 scheduled workflows (117 enabled), 230+ Python scripts, 50+ skills, 82 tracked assets across 5 groups, 13 report types, 12+ data sources.
- Infrastructure: one Mac mini, ~$55/month budget cap, actual spend ~$7/month.

This is research and education only. Not investment advice. All output is bullish/neutral/bearish scenario labels — never a signal, never a pick, never a guarantee.

Free weekly research: https://tradingmapclaw.substack.com
Full system + products: https://www.tradingmapclaw.com
Disclaimer: https://www.tradingmapclaw.com/legal/disclaimer

### Full Script (~1200 words)

[SCREEN: dashboard/terminal opening view. No face on camera throughout — voiceover only.]

Hi. I'm Mickey. I'm not going to be on camera in this video — what you're going to see is my screen, because I want to actually show you the system instead of just talking about it.

Quick context, because it explains why this system exists at all. I have one working hand. I've had eight surgeries. I live with a permanent ostomy. I spent my career in bank back-office operations — Wells Fargo, Deutsche Bank, UBS, JPMorgan, eToro — settlement, reconciliation, maker-checker controls. Not the trading floor. The machinery underneath it.

In May 2026, I had zero coding background. None. And I started building a research system for myself anyway, because I wanted to track markets I care about without paying for a stack of separate subscriptions, and because I wanted to see if the discipline I'd learned in bank operations — never trust one number without a second check — could actually be built into software.

[SCREEN: architecture diagram or workflow scheduler view]

Two months later, here's what exists. I call it TradingMapClaw. Let me walk through the architecture first, because that's the part that actually matters, not the story.

Before I get into the diagram, I want to explain the actual problem I was trying to solve, because it shapes every decision that follows. When you use a single AI model to analyze a stock, or any asset, you get one voice, and that voice can sound completely confident whether it's right or wrong. In bank operations, we never let that happen with money. A settlement instruction doesn't move forward because one person felt confident about it — it moves forward because an independent second person checked it against source data and confirmed it. I wanted that same discipline applied to research output, not just to trade processing. That's the entire reason this system has the shape it has.

The system runs on what I call a dual-engine design. Engine 1 is Hermes Agent — it's the orchestrator. It runs fundamentals analysis, valuation work, insider activity tracking, and a macro, industry, and sentiment pass. That's the first engine's job: build the primary research view.

Engine 2 is Codex, and its role is different on purpose. It works independently — running technicals, capital flow analysis, and options analysis — but it has one more job that's actually the most important part of this whole system: it's required to cross-verify Engine 1's numbers before anything ships. If Engine 1 says something and Engine 2's independent check disagrees, that disagreement gets surfaced. It doesn't get quietly smoothed over into one confident-sounding answer.

[SCREEN: council/model routing view]

Above both engines is what I call the Multi-Model Council. Three models: DeepSeek V4 Pro, GLM-5.2, and GPT-5.6. There's also a local model, Qwen3 14B, that closes out the fallback chain if something upstream isn't available. When the council can't agree, there's a fixed tiebreaker order — DeepSeek first, then GLM-5.2, then GPT-5.6 — so disagreement has a defined resolution path instead of an arbitrary pick.

Here's the structural piece I want to be precise about, because I've been sloppy about this in early drafts of my own documentation and I'm correcting it here: there are two engines, not three. What runs in three parts is the analysis itself — three weighted passes per research cycle. Pass A is fundamentals, weighted 40%, run by Engine 1. Pass B is technicals plus cross-verification, weighted 35%, run by Engine 2. Pass C is macro and sentiment, weighted 25%, run by Engine 1. Two engines, three passes. I'll never call this "three engines" anywhere, because it isn't, and getting that wrong would misdescribe how the actual verification works.

I'll actually admit something here: some of my own early tutorial PDFs from the first week of July still say "three-engine" in a couple of places, because that's how I was thinking about it before I tightened the language. I've flagged that in a version note in those documents rather than pretending it never happened, and the next edition unifies the wording properly. I'd rather tell you about a documentation mistake than let you find it yourself and wonder what else might be inconsistent.

[SCREEN: scheduler / cron dashboard view, scrolling through job list]

Now, the scale of what's actually running. As of this version — v2.0, dated July 12, 2026 — the system executes 118 scheduled workflows, and 117 of those are currently enabled. Behind those workflows are 230-plus Python scripts and more than 50 skills modules. It tracks 82 assets across 5 groups, and produces 13 distinct report types, pulling from more than 12 data sources.

[SCREEN: cost dashboard or budget tracker]

And the infrastructure question people always ask: what does this cost, and what does it run on? It runs on one Mac mini. Nothing else — no cloud cluster, no rented GPU farm. I set myself a budget cap of $55 a month as a discipline device, a ceiling I never wanted to quietly blow past. Actual spend has run closer to $7 a month. That gap exists because the architecture is built around two engines that specialize and check each other, rather than one model being called over and over for everything — and because the scheduling and caching layer is deliberately designed to avoid redundant calls.

I think it's worth being honest about what that number does and doesn't mean. Seven dollars a month is genuinely what the API usage costs on top of hardware I already owned before this project existed. It doesn't include my own time, and it doesn't include the cost of the Mac mini itself, since I already had it for other things. I'm not claiming anyone can replicate a system like this for seven dollars starting completely from scratch with no hardware and no time invested — I'm telling you what my actual marginal running cost is, because I think vague claims about "cheap AI systems" are exactly the kind of thing that erodes trust in this space, and I'd rather over-explain the number than let it sound like a magic trick.

[SCREEN: sample report / scenario label output]

Now, the part I want to be most careful about in this whole video: what this system actually outputs. Every report ends in a scenario label — bullish, neutral, or bearish. That's it. Never a buy call. Never a sell call. Never a "signal." Never a "pick." Never a guarantee about performance. This is a research and education tool. It is not investment advice, not personalized advice, not a brokerage, not fund management, and it doesn't execute trades, auto-trade, or copy-trade anything. The sample data you'll see in the free Weekly Market Radar is refreshed weekly and labeled that way — I never call anything "live" that isn't.

[SCREEN: build log / Substack view]

I write about both halves of this project every week — the engineering, in detail, and the story behind why I built it the way I did. If you want the free layer, the Weekly Market Radar and the Engine Disagreement Brief are both free on the Substack. If you want to understand exactly how this system was built, layer by layer, I've put together a tutorial series that walks through it — starting with the beginner volume on the $55 AI research stack concept, through to the advanced solo-operator blueprint.

[SCREEN: closing, tradingmapclaw.com homepage]

This system doesn't know or care that it was built by someone with one working hand. It just runs — every workflow, every cross-check, every scenario label — the same way it would if anyone else had built it. That's actually the whole point for me. Ability first, background second.

Links to everything are in the description. Thanks for watching.

---

## 3. Follow-Up Video Outlines (3)

### Outline A: "Why I Built Two AI Engines Instead of One (And What Happens When They Disagree)"
- Hook: one confidently wrong AI answer vs. two engines that catch each other.
- Segment 1: the bank-operations origin of maker-checker thinking (screen: notes/diagram, no personal footage needed).
- Segment 2: live-walkthrough of a scenario where Engine 1 and Engine 2 disagree on a data point — show how the system surfaces it rather than resolving it silently.
- Segment 3: the council tiebreaker order and why it's fixed rather than arbitrary.
- Close: this is a verification pattern, not a performance claim — link to deep-analysis page and disclaimer.
- CTA: tradingmapclaw.com/deep-analysis, Substack build log.

### Outline B: "The Real Cost Breakdown: Running 118 Workflows for $7/Month"
- Hook: budget cap ($55) vs. actual spend (~$7) — explain the gap honestly.
- Segment 1: screen-recording of the scheduler dashboard, walking through workflow categories.
- Segment 2: where the cost actually goes (API calls, data sources) and why the dual-engine design reduces redundant calls.
- Segment 3: hardware — one Mac mini, no cloud cluster, what that constrains and what it doesn't.
- Close: honest caveat that this is a personal-scale project, not an enterprise deployment claim.
- CTA: tradingmapclaw.com, tutorial Vol.1 ($19) for people who want the full breakdown.

### Outline C: "From Zero Coding Background to a 118-Workflow System: The AI-Assisted Build Process"
- Hook: I couldn't type fast enough with one hand to write this the traditional way — here's what the actual workflow looked like.
- Segment 1: screen-recording of a real AI-assisted coding session (describe intent → review output → test → ship), explain the review discipline carried over from bank ops.
- Segment 2: mistakes/corrections along the way — kept honest, no fabricated anecdotes, framed generally (e.g., "the discipline of reading every line before shipping caught issues early").
- Segment 3: how this generalizes — advice for anyone starting a solo AI-assisted build with no engineering background.
- Close: pull to the System Build Log and the tutorial series for people who want the full narrative.
- CTA: tradingmapclaw.substack.com, tradingmapclaw.com/products.

---

*All content above is DRAFT pending Mickey's review and approval before posting/recording. No fabricated metrics, customers, testimonials, or returns are included. CTAs point to tradingmapclaw.com or the Substack only.*
