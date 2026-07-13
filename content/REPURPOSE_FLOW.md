<!-- status: DRAFT — requires Mickey approval before publishing -->
# Repurpose Flow — One Mother Brief → 9 Derivatives

**Source:** each week's `MOTHER_CONTENT_TEMPLATE.md` instance ("Weekly Market Intelligence Brief").
**Rule:** every derivative below is a *transformation* of the mother brief's content, not new research. If a derivative needs a claim the mother brief doesn't contain, go back and add it to the mother brief first — never invent content at the derivative stage.
**Compliance:** all 9 red lines from `FACTS.md` §5 apply identically at every derivative stage. Scenario-label-only, no fabricated data, as-of dates preserved, DRAFT-by-default, no personal position disclosure, "cron" never used in Chinese copy, no fabricated testimonials.

---

## Conversion Rules Table

| # | Channel / Format | Length | Tone | CTA | Hard "don'ts" for this channel |
|---|---|---|---|---|---|
| 1 | X thread (8–12 tweets) | ~280 chars/tweet, 8–12 tweets | First-person, punchy, story-forward but factual | tradingmapclaw.com or Substack, once at the end | Never split one number across two tweets in a way that changes its meaning; never drop the as-of date when citing a figure |
| 2 | X single post | ≤280 chars | One idea, one number, one link | Single link, tradingmapclaw.com or /radar | No thread-only nuance compressed into a misleading one-liner; if the point needs a caveat, don't post it standalone |
| 3 | LinkedIn long-form article | 600–900 words | Professional, first-person, reflective, still factual | 1–2 links at the end (site + Substack) | No jargon dump without the "what it will never do" paragraph; no implying career employers endorse the product |
| 4 | Reddit post (subreddit-specific) | 300–600 words | Builder-transparent, disclose affiliation up front, no promotion-first | One link, offered not pushed, near the end | Never cross-post identical text to 2 subreddits same day; always include "check subreddit rules" gate before posting; disclose you're the builder in the first 2 sentences |
| 5 | HN Show HN comment/follow-up | 150–400 words | Technical, skeptical-audience-ready, precise about engine-vs-pass distinction | tradingmapclaw.com, used sparingly | Never editorialize about performance/returns; must survive stress-testing of every number cited |
| 6 | YouTube script outline | 150–300 word outline (full script written separately if greenlit) | Screen-recording voiceover style, first-person, no face | End-card links to site + Substack | No claims not verifiable on-screen; label all sample data on-screen as "sample" |
| 7 | Newsletter (Substack short digest) | 400–700 words | Direct, conversational, weekly-cadence voice | Reply-to or site link | Must preserve mother brief's as-of dates and Engine Disagreement Spotlight if referenced |
| 8 | Substack long-form (System Build Log style) | 800–1400 words | Detailed, engineering-narrative, first-person | 1 link at close | No compressing the disagreement mechanism into a vague "the system checks itself" — must be specific |
| 9 | GitHub build-log / Discussion entry | 200–500 words | Plain, technical, versioned | Link to deep-analysis or Substack | Must cite the FACTS.md version number if any system numbers are mentioned; no marketing tone |

---

## Transformation Steps (per derivative)

1. **Pull, don't paraphrase-drift.** Copy the exact figures, as-of dates, and scenario labels from the mother brief. Do not "round up" or restate a number more impressively than the source.
2. **Trim to the channel's length/tone**, using the table above. Cutting content is fine; adding new claims is not.
3. **Re-check the 9 compliance red lines** against the trimmed version — trimming sometimes accidentally drops a caveat (e.g., cutting "illustrative" off a sample-data sentence). Read the derivative alone, as if the mother brief didn't exist, and confirm it still reads compliant.
4. **Set status** using the same status vocabulary as `FOUR_WEEK_SCHEDULE.csv`: READY / NEEDS FACT CHECK / NEEDS MICKEY APPROVAL / BLOCKED / OUTDATED.
5. **Route to the manual publish SOP below** — no derivative auto-publishes, ever.

---

## Manual Publish SOP (hard gate — applies to every channel)

1. Drafter (Mickey or delegated writer) finishes the derivative and sets status to `NEEDS MICKEY APPROVAL` at minimum for anything customer-facing.
2. Mickey reviews against: (a) FACTS.md current version, (b) the specific channel's "don'ts" column above, (c) whether subreddit/platform rules have changed since last check (Reddit especially — rules and self-promo windows shift).
3. Mickey explicitly approves — in writing (comment, checklist tick, or direct message) — before any posting action. Approval is per-post, not per-kit or per-week: an approved tone on one post does not pre-approve a later edit or a different channel's version of the same idea.
4. **Automated "click Publish" is prohibited system-wide.** No scheduling tool, cron job, or agent may submit a post to any external platform (X, LinkedIn, Reddit, HN, YouTube, Product Hunt, GitHub, ESP/Substack) without a human manually clicking Publish/Send after Mickey's explicit go-ahead. Scheduling tools may be used to *draft and queue*, never to auto-fire.
5. After posting, log the actual publish date/time and URL back into the row's `notes` field in `FOUR_WEEK_SCHEDULE.csv` (or successor tracking sheet) for audit continuity.
6. If a platform's community rules block a post (e.g., subreddit self-promo window closed), mark it `BLOCKED` and reschedule rather than force-posting elsewhere same-day.

---

## Cross-Channel Spacing Reminder (from `content/launch-kit/INDEX.md` hard rules, still binding for steady-state cadence)

- Never post more than one Reddit derivative within the same 24-hour window; never post identical (even lightly reworded) text to two subreddits same day.
- Check current subreddit rules immediately before each Reddit post, not just once.
- All CTAs terminate at tradingmapclaw.com or tradingmapclaw.substack.com only — no third-party affiliate links in any derivative.
