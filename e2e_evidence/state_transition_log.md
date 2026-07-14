# Workspace E2E State-Transition Log — 2026-07-14

Fixture: ws-asset-testz-fixture (TESTZ — synthetic, not a real security). Never published to Production.

| step | actor | action | state | evidence |
|---|---|---|---|---|
| 1 | Hermes | generate candidate | `HERMES_READY` (codex=PENDING) | e2e_evidence/candidate_testz.json |
| 2 | Codex | independent verify (schema+compliance+dual-PASS+FRESH) | `APPROVED_CANDIDATE` (rc0) | e2e_evidence/codex_report_testz.json |
| 2b | Codex | red-line negative test | `BLOCKED` (rc4) | e2e_evidence/codex_report_bad.json |
| 2c | Codex | missing-field negative test | `NEEDS_FIX` (rc3) | e2e_evidence/codex_report_nofix.json |
| 3 | GitHub Actions | CI verify-all + workspace gates on branch | (CI conclusion) | run id below |
| 4 | Cloudflare Pages | Preview deploy (pr branch) | `PREVIEW` | preview URL below |
| 5 | smoke | fixture NOT on Production | proof | prod 404 for fixture path |
| 6 | cleanup | delete branch + fixture files | removed | git log / ls |

LIVE gate: APPROVED_CANDIDATE is NOT LIVE. LIVE requires dual-PASS + FRESH AND a deliberate publish
(merge to main). The fixture is intentionally stopped at PREVIEW and never merged.
