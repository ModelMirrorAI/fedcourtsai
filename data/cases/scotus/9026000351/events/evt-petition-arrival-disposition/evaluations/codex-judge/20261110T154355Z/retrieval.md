# Evaluator retrieval

Read the evaluation contract and schemas; this event's event.yaml and outcome.json; the case-level context, November 9 snapshot, questions presented, document manifest, and relevant petition and appendix passages; and every blinded candidate's prediction, rationale, forecast, retrieval note and harness-captured retrieval log. No committed predictor tree, identity map, candidate-identifying history, or labeling-measurement artifact was consulted.

Read the current committed statpack for context, then assessed each candidate's base-rate use against its reconstructed prediction-time build rather than comparing across refreshes:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All three resolved to build `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`, landed September 26, 2026, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, with no recorded digest or alternative build. Consulted the reconstructed sal-v4 table and exact JSON rates: the displayed prior-Term baseline reached pool is 638 / 12,720 = 0.05015723270440252. These are statpack-history lookups, not corpus queries, and emit no ranged-corpus transfer line.

No evaluator corpus query, open-events call, CourtListener MCP lookup or web search was made. Candidates' own logged retrievals were reviewed as evidence and were not repeated. No external case facts or opinion text were fetched. Validation uses only the local schemas and model definitions.
