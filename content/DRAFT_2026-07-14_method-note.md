# Method note: why every public number carries an as-of date

DRAFT — requires Mickey approval before publishing.

I run a research system from a single Mac mini. One hand, one backpack, one machine. When I publish a number — 118 scheduled workflows, 230 Python scripts, 82 tickers — that number is already decaying. By the time you read it, a cron job may have been disabled, a script refactored, a ticker dropped from coverage. This is not a bug. It is a feature of running something that actually runs.

The as-of date is the only honest thing on the page.

Here is the system, stamped July 14 2026: 118 scheduled workflows, of which 117 are enabled and one is paused. 230-plus Python scripts. 50-plus SKILL.md modules encoding research logic that would take a human analyst a full day to replicate manually. 82 tickers across five watchlist groups — A through E — with 75 unique underlying instruments after deduplication. 13 distinct report types generated from 12 data sources. Monthly operating cost runs approximately $7 against a $55 budget cap. Everything runs on one Apple Silicon Mac mini. English output goes to Telegram; Chinese output goes to Feishu.

Those numbers will be wrong within a week. Possibly within a day.

The problem with publishing system stats is that they look like a spec sheet. They are not. A spec sheet describes what was designed. These numbers describe what was running at the moment I checked the dashboard. The distinction matters because this system is a live organism, not a product roadmap. Scripts get added when a new data source breaks. Tickers get promoted or demoted based on signal quality. Workflows get disabled when a data provider rate-limits us into silence. Nothing is static except the hard constraint: WATCHLIST_ONLY. No broker API. No order execution. No wallet connected. The system observes and analyzes. It does not act on capital.

I learned the distinction between design and runtime the hard way. In earlier versions of the system, I published numbers without dates. Someone screenshotted a post mentioning "500-plus scripts" and it circulated for months after the actual count had dropped during a consolidation cycle — I had merged redundant modules, deleted dead code paths, and the real number was closer to 200. Someone else built an assumption around an architecture label that had already been replaced. The current architecture uses two engines: Hermes Agent as orchestrator handling fundamentals, macro, and sentiment; Codex running on GPT-5.6 as independent verifier for technical and flow analysis. A multi-model council — DeepSeek V4 Pro, GLM-5.2, GPT-5.6, plus a local Qwen3 14B serving as free fallback — votes on disagreement. The slogan is not marketing copy; it is operational observation: one model can be confidently wrong. Two engines catch it. A council of three decides.

The old label — a term tied to the previous architecture — outlived that architecture by several months. That is how misinformation breeds in public research: not through malice, but through timestamp failure. A reader in October reads a July number and treats it as current. A journalist references a screenshot from six months ago. A potential user builds expectations around a feature set that no longer exists. The number was true when written. It became false while circulating.

Every public number I publish now carries an as-of date because I want you to distrust it. Not distrust me — distrust the number's permanence. If you see "82 tickers" in a post from July and it is now October, assume the count has shifted. If you see "$7 per month" referenced without a date, ask which month. If you see a product price without a timestamp, check the current page at tradingmapclaw.com before forming an expectation.

This discipline extends into every research output the system generates. When a radar scan or market structure brief lands in the Telegram channel, every data point carries an as-of timestamp. If Yahoo Finance rate-limits mid-pull, the field reads DATA_UNAVAILABLE — not an estimate, not a stale cache, not the last-known value dressed up to look current. I would rather ship a report with a visible hole than ship a report with a number I cannot timestamp. The multi-model council operates under the same constraint: each engine's output is stamped with its model version and generation timestamp, because an insight produced by GPT-5.6 on Monday morning carries different weight from the same insight produced by the same model on Friday afternoon after a macro event reshuffles every correlation matrix.

This is not academic rigor for its own sake. It is operational necessity. When you run 117 scheduled workflows unattended through the night, you need to know which run produced which number. When a subscriber asks why a signal shifted between two reports, you need to trace it to a model update, a data refresh, or a human override. When the fallback chain activates — GLM-5.2 stepping in because GPT-5.6 timed out, DeepSeek V4 Pro taking over because GLM-5.2 returned an unparseable response, Qwen3 14B running locally as the last line of defense — every hop in that chain is logged with a timestamp, a model ID, and a latency measurement. Without as-of discipline, every investigation starts with "well, it depends when you looked." With it, you can reconstruct the exact state of the system at the exact moment a number was produced.

For readers consuming the output, the rule is simple: treat every number as a measurement, not a fact. Measurements decay. Facts persist. The system reports measurements, and measurements are only true at their as-of date. If you need the current state, check the current source — not a post from last month.

What exists right now at tradingmapclaw.com/products (as-of July 14 2026):

Three tutorial volumes — The $55 AI Research Stack (Beginner), Building the Dual-Engine System (Intermediate), and The Solo-Operator Blueprint (Advanced) — at $19 each. The Solo-Operator Blueprint Complete Bundle of all three volumes plus extras at $49. The Engineering Patterns Bundle of seven production skill packs at $79. All five digital products are live on Payhip with instant download.

Five Skill Minis — Financial Research Checklist, Earnings Research Prep, Dual-Engine Verification Prompt, Evidence vs. Counter-Evidence Matrix, and Market Research Journal Template — at $9 each, also live on Payhip.

The Skills Library subscription at $29 per month remains waitlist-only. No checkout link exists because the pipeline that would deliver monthly skill updates is not yet production-ready. When it is, the status will change and the as-of date on that status will update.

Consulting is live via email application: Operator Consulting at $200 per 60-minute session, Research-System Audit at $399 for a written report, and Architecture Blueprint Session at $699 for a deep-dive design engagement. Manual confirmation required — no instant checkout — because every research setup is different and I verify fit before committing time.

This tiered structure reflects operational reality, not marketing segmentation. Some deliverables are automated and scalable. Some require ongoing maintenance. Some are irreducibly human. Each tier carries a different failure mode, and the as-of date on pricing and availability tells you which tier you are looking at.

The code runs on one machine, operated by one hand. One hand, one bag, one system. Not pity. Visibility.

Research & education only. Not investment advice.