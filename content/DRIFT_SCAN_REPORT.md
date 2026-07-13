# Drift Scan Report — Launch Kit 20260712

**Scan date:** 2026-07-13
**Scanned by:** Sub-agent B, per `docs/SPEC_MEDIA_PHASE2.md`
**Fact baseline:** `/home/user/workspace/repo/tradingmapclaw-website/FACTS.md` (v2.0.1, as-of 2026-07-13)
**Input (read-only):** `/home/user/workspace/tmc/handoff-bundle/marketing/launch-kit-20260712/` (9 files: INDEX.md, x-twitter.md, linkedin.md, reddit.md, hackernews.md, github.md, youtube.md, producthunt.md, emails.md)

## Method

Every file was read in full. Then targeted `grep` passes were run across the full kit for each drift signal category named in the SPEC:
1. Legacy engine framing (three-engine/三引擎), legacy counts (119/115 jobs, 502+/500+ scripts, 93+/50+ skills misprint), legacy model name (GPT-5.5)
2. Legacy prices ($149, $99, $29 single-tutorial)
3. Fabricated customers/earnings/testimonials, "guaranteed"/稳赚, false "real-time" data claims
4. Buy/sell instruction language, "high conviction"
5. "Buy now" language for products not yet live on Payhip (should be waitlist/preorder/coming soon per FACTS §3)

## Summary

| Category | Instances found | Files affected |
|---|---|---|
| Legacy engine/job/script/skill counts, "three-engine", GPT-5.5 | 0 live drift (2 informational disclosures of a *known issue elsewhere*, not drift in this kit) | github.md, youtube.md (disclosure only) |
| Legacy prices ($149/$99/$29) | 0 | — |
| Fabricated customers/earnings/testimonials/guarantees | 0 | — |
| Buy/sell instruction language, "high conviction" | 0 | — |
| **Service pricing/name mismatch vs FACTS.md §3 canonical service table** | **3** | emails.md (×2), reddit.md (×1) |
| **"Buy now" / "live now" framing for products not yet on Payhip** | **2** | emails.md (×2) |

**Total confirmed drift instances requiring fix: 5** (across 2 files: emails.md, reddit.md)

The kit is, overall, in very good shape — it was clearly built against an already-updated FACTS.md v2.0 baseline (118/117 workflows, 230+ scripts, 50+ skills, 82 assets/5 groups, 13 report types, 12+ data sources, GPT-5.6, ~$7/mo actual vs $55 cap all appear correctly and consistently across x-twitter.md, linkedin.md, hackernews.md, producthunt.md, github.md, youtube.md). The drift that does exist is concentrated in the **service/consulting pricing table** and in **premature "live" checkout language** in `emails.md`, plus one echo of the same pricing table in `reddit.md`.

---

## Confirmed Drift — Detail

### D1. Service pricing/name mismatch vs FACTS.md §3

FACTS.md §3 canonical service table (only three consulting/service SKUs exist):

| Product (FACTS.md) | Price |
|---|---|
| System Architecture Review (咨询) | $200 |
| Dual-Engine Setup Session (咨询) | $399 |
| Full Pipeline Blueprint (咨询) | $699 |

**D1-a — `emails.md` line 134**
> "**Services, booked by email:** Research Workflow Audit ($399), System Architecture Review / Blueprint Session ($699), and Technical Consulting ($200/hr) — all scoped as technical/architecture services, not investment advice."

- Problem type: fabricated/renamed SKUs with prices reassigned — "Research Workflow Audit" and "Technical Consulting" do not exist in FACTS.md; "System Architecture Review" is real in FACTS.md but priced at $200, not $699.
- Fix: replace with the three real FACTS.md services and correct prices: System Architecture Review ($200), Dual-Engine Setup Session ($399), Full Pipeline Blueprint ($699).

**D1-b — `emails.md` line 264**
> "**If you want architecture help for your own project:** a Research Workflow Audit ($399), a System Architecture Review ($699), or hourly Technical Consulting ($200/hr) — booked by email, scoped as technical/architecture services only, not investment advice."
- Same problem as D1-a, in Welcome Email 4.
- Fix: same substitution as D1-a.

**D1-c — `reddit.md` line 78**
> "- **Services** — a Research Workflow Audit ($399), a System Architecture Review ($699), and hourly Technical Consulting ($200/hr), all booked by email, explicitly scoped as technical/architecture services, not investment advice."
- Same problem, in the r/SaaS post's business-structure bullet list.
- Fix: same substitution as D1-a.

### D2. Premature "buy now" / "live" checkout language (Payhip not yet up)

FACTS.md §3: *"Payhip 上架完成前：不得写 'Buy now available'；JSON-LD availability = PreOrder"* and the per-product status column reads *"文件已完成；Payhip 未上架 → 网站 CTA = waitlist/PreOrder"* for all three tutorials + bundles.

**D2-a — `emails.md` line 122**
> "**Digital products, live now:**"
- Problem type: "live now" framing for tutorials that are not yet purchasable (Payhip storefront not live per FACTS.md).
- Fix: reframe as "Digital products (waitlist/preorder — Payhip checkout launching soon):" and adjust surrounding copy to not assert an active purchase flow.

**D2-b — `emails.md` line 136**
> "Everything is delivered through Payhip with automatic delivery. Details and purchase links: https://www.tradingmapclaw.com/products."
- Problem type: asserts an active, working Payhip delivery/purchase flow, when Payhip is not yet live (FACTS.md §3: "Payhip 未上架").
- Fix: reframe to describe the intended future delivery mechanism without claiming it is live today, and route to waitlist/preorder instead of "purchase links."

---

## Non-Drift Items Reviewed and Cleared

These were checked against the SPEC's drift signal list and found to be **compliant, not drift** — logged here for completeness per the "no空泛" requirement:

- **github.md lines 72–73** and **youtube.md line 65**: both reference "three-engine" — but only as an *in-kit disclosure* that some early Tutorial PDFs (outside this kit, not modified by this task) still contain the legacy "three-engine" phrasing, explicitly flagged as a documentation issue to be fixed in the next tutorial edition. This is the kit correctly *calling out* known drift elsewhere, not committing the drift itself. No fix applied; left as-is (matches SPEC's "只修复漂移" — this is not drift, it's an accurate meta-disclosure).
- All numeric claims (118/117 workflows, 230+ scripts, 50+ skills, 82 tracked assets in 5 groups, 13 report types, 12+ data sources, ~$7/mo actual vs $55 cap, GPT-5.6, DeepSeek V4 Pro, GLM-5.2, Qwen3 14B) — checked file-by-file across all 9 files, consistent with FACTS.md v2.0.1, no legacy figures (119/115, 502+/500+, 93+) or GPT-5.5 found anywhere in the kit.
- Tutorial pricing ($19 each, $49 bundle, $79 Patterns Bundle) — consistent with FACTS.md §3 across x-twitter.md, linkedin.md, reddit.md, hackernews.md, emails.md.
- No buy/sell/hold instruction language, no "guaranteed"/"beat the market"/"alpha", no "high conviction" (all scenario-label-only language throughout).
- No fabricated customers, testimonials, or return/performance numbers anywhere in the kit.
- No false "real-time" data claims — emails.md explicitly disclaims "no real-time claims" and labels all sample data as illustrative/sample, never "live."
- Bank names (Wells Fargo, Deutsche Bank, UBS, JPMorgan, eToro) are consistently framed as career history only, with explicit no-endorsement disclaimers where relevant (emails.md Email 2 footer).

## Files With Zero Drift (no fix needed on copy, only header status comment added)

- INDEX.md
- x-twitter.md
- linkedin.md
- hackernews.md
- github.md
- youtube.md
- producthunt.md

## Files Requiring Fixes

- emails.md — 3 fixes (D1-a, D1-b, D2-a, D2-b — 4 line-level edits across 3 issue instances, see above; note D1-a and D2-a/b are distinct issues in overlapping regions)
- reddit.md — 1 fix (D1-c)
