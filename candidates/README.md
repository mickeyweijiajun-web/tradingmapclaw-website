# Candidate verification inbox

This directory is not deployed. Hermes may submit `HERMES_READY` JSON candidates here
for the GitHub Actions `codex-verify` job. The job runs the deterministic independent
verifier and uploads structured reports. A candidate must not be copied into
`site/data/workspace/` until that report is approved and the production JSON is stamped
`verification.codex.result=PASS`.
