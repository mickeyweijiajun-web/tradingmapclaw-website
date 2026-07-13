<!-- status: DRAFT — requires Mickey approval before publishing -->
# TradingMapClaw Partnership Policy

**Owner:** Mickey Wei
**Applies to:** all inbound and outbound partnership, sponsorship, affiliate, and collaboration discussions for TradingMapClaw.
**Fact baseline:** `FACTS.md` — every commitment made in a partnership must remain consistent with the current version of that file. No partnership may require a change to FACTS.md's numbers or compliance boundaries.

This document only governs **evaluation and decision-making** for partnerships. It does not authorize outreach. See `PARTNER_PROSPECTS.csv` for the current research-only candidate list — status `CANDIDATE` means researched, not contacted.

---

## 1. Accepted Partnership Types

| Type | Description | Conditions |
|---|---|---|
| **Educational content collaboration** | Guest posts, co-authored explainers, cross-linked build-log entries, podcast/newsletter features focused on architecture, verification methods, or the accessibility/build story | Must stay within FACTS.md §5 compliance red lines; no scenario labels reframed as calls to action by the partner |
| **Open-source collaboration** | Code contributions, shared tooling, joint write-ups on engineering patterns (scheduling, cross-verification, cost control) | Only for components that are already public or explicitly approved for release by Mickey; no sharing of internal system credentials or unreleased architecture details |
| **Affiliate referrals with clear disclosure** | Recommending a third-party tool/service (or being recommended) where the commercial relationship is disclosed per `SPONSORSHIP_DISCLOSURE.md` | Disclosure must be visible on first mention, not buried in a footer; TradingMapClaw's own scenario labels and research output are never the subject of an affiliate arrangement |

## 2. Not Accepted (This Round)

| Type | Why not |
|---|---|
| **Display advertising** | Not part of the current monetization model; revisit only after Mickey explicitly changes strategy in a future FACTS.md revision |
| **Endorsement-for-payment on products with promised returns** | Directly conflicts with FACTS.md §5 (no guaranteed returns, no "beat the market" language) — cannot be reconciled regardless of payment size |
| **Undisclosed sponsorship** | Violates `SPONSORSHIP_DISCLOSURE.md` by definition; any partner unwilling to accept visible disclosure is disqualified immediately |
| **Any request for user/subscriber data sharing** | TradingMapClaw does not sell, trade, or share subscriber/user data with any partner under any structure |

## 3. Evaluation Criteria

Every candidate in `PARTNER_PROSPECTS.csv` is scored against these before any outreach is authorized:

1. **Audience match** — does the partner's audience overlap with "solo builder + AI research system" readers (AI engineering, quant/systematic research, personal finance education, disability-in-tech, indie-builder communities)? Weak overlap = lower priority regardless of reach.
2. **Compliance risk** — could the partnership create pressure (implicit or explicit) to make return claims, imply endorsement by former employers, or blur scenario labels into advice? Any material risk here is disqualifying, not just a "risk" note.
3. **Workload** — can this be executed without diverting time from the core research system and its weekly cadence? A partnership that requires ongoing production work beyond a single collaboration should be flagged for explicit time-budget approval.
4. **Quote / rate floor** — for anything involving payment (either direction), the floor is: no paid sponsorship placement accepted below a rate that would materially compromise editorial independence, and no payment made for endorsement of TradingMapClaw's research quality or system numbers (those must always be independently verifiable against FACTS.md, not "bought").

## 4. Decision Process

```
Candidate identified (research only, e.g. via PARTNER_PROSPECTS.csv)
        │
        ▼
Evaluate against Section 3 criteria ── fails compliance risk? ──► Reject, log reason
        │ passes
        ▼
Draft a one-page brief: audience fit, proposed collaboration type (Section 1),
compliance check against FACTS.md §5, and workload estimate
        │
        ▼
Mickey reviews the brief and decides: Approve outreach / Reject / Hold for later
        │
        ▼
If approved: Mickey (or someone Mickey explicitly designates) sends outreach —
no automated or agent-initiated outreach ever
        │
        ▼
If a deal proceeds: disclosure language finalized per SPONSORSHIP_DISCLOSURE.md
before any joint content goes live
```

**No commercial outreach email may be sent without this process completing and Mickey's explicit approval.** Research and candidate evaluation (as done in `PARTNER_PROSPECTS.csv`) does not constitute approval to contact anyone.

## 5. Review Cadence

This policy should be revisited whenever FACTS.md is revised (particularly §3 pricing/product status or §5 compliance red lines), and at minimum once per quarter as the partnership pipeline develops.
