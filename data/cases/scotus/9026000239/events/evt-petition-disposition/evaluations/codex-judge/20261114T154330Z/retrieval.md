# Evaluator retrieval record

Read the evaluation contract and schemas, this event's definition and outcome, case-level context and November 13 snapshot, the three blinded candidates' predictions/rationales/forecast documents/retrieval notes, and their harness-captured retrieval logs. Consulted staged questions presented and selected petition, opposition and reply passages. Checked that no opinion slot was staged. No candidate identity was sought, and no committed prediction tree, prediction history, alias map or labeling-measurement artifact was read.

## Historical statpack context

Reconstructed the historical pack for each alias using the permitted statpack-history helper, with package synchronization disabled and offline mode enabled; no packages were installed:

- `UV_NO_SYNC=1 UV_OFFLINE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` initially failed because the default uv cache directory was read-only.
- `UV_CACHE_DIR=/tmp/uv-evaluate-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` succeeded.
- `UV_CACHE_DIR=/tmp/uv-evaluate-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` succeeded.
- `UV_CACHE_DIR=/tmp/uv-evaluate-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` succeeded.

All three selected build `a14b36a1e190a86d6a01df2ce410f5f9e54fb98b`, landed October 12, 2026 at 17:55:06-04:00, digest `sha256:84a5c25d4bf0a2a70ba5c6e9392e2e21d43ed5b794de0ae59c27cf1973ad0e7e`, with no alternative build. Read the recovered sal-v4 description and prior-Term federal risk-set rows to assess the candidates' historical-anchor use. No new case facts were obtained, and no evaluator baseline was inserted into any evaluation.

No corpus query or open-events lookup was made, so there is no ranged-corpus transfer line. No CourtListener lookup or web search was performed. All case-specific grading rests on the provisioned record. Local schema validation uses the preinstalled system Python jsonschema package; the project virtual environment does not contain that package.
