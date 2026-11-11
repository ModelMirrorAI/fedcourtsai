# Evaluator retrieval record

Read the evaluation contract and schemas, this event's definition and outcome, the provisioned case context and resolved docket snapshot, questions presented, selected petition passages and appended lower-court reasoning, the document manifest, and all three blinded candidates' predictions, rationale documents, forecast documents, retrieval notes and captured retrieval logs. No candidate identity lookup, other evaluator output, external case retrieval, corpus query, CourtListener lookup or web search was performed.

To assess calibration against the material available when the predictions ran, reconstructed only the statpack's own history using the contract-authorized commands:

1. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73522552/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
2. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73522552/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
3. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73522552/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

Each resolved prediction run 20261029T142045Z to build 7bcde3b105cb212283905eda17b827efc188e80c, landed 2026-10-28T13:56:30-04:00, digest sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641. All recorded digests and alternative_sha fields were null. Inspected the reconstructed sal-v4 prior-Term baseline rows to assess candidate statements; no evaluator baseline or skill score was computed. These commands reported no ranged corpus reads transfer line because they reconstruct repository statpack history rather than query the corpus.

Local schema validation uses the installed Python jsonschema validator, not whole-tree validation; no packages were installed.
