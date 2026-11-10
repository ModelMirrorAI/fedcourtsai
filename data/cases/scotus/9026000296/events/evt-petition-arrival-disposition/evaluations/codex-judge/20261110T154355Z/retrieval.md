# Evaluation retrieval log

Read the evaluation contract and schemas, this event's event.yaml and outcome.json, the case-level decided context and November 9 snapshot, provisioned document metadata and questions presented, relevant petition and appendix passages, and all three blinded candidates' prediction, rationale, forecast, retrieval note and harness-captured retrieval log. No candidate identity source or committed prediction tree was consulted. No opinion or denial-order text was fetched to fill a missing staged slot.

## Historical statpack reconstruction

Ran these permitted statpack-history lookups to check candidates' use of their prediction-time base-rate context rather than compare them with a later build:

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000296/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000296/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000296/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three succeeded and returned build `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`, landed September 26, 2026, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, with no alternative build. Read the recovered sal-v4 segment table, shared by the three reconstructions, to verify private baseline reached-row selection and strictly-prior Terms. No new numerical baseline or Brier skill was supplied; those are harness-stamped.

These are statpack-only history lookups, not corpus queries, and printed no ranged-corpus transfer line. No `fedcourts query` or `open-events` command, CourtListener MCP lookup, or web search was made by this evaluator. Candidates' historical lookups were inspected as evidence in their staged logs, not reissued.
