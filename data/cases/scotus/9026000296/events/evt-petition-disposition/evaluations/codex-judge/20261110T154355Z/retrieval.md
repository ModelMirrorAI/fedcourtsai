# Evaluator retrieval

Read only this cell's evaluation contract/schema, staged event/outcome, case-level context and terminal snapshot, provisioned QPs and selected petition/appendix passages, and each blinded candidate's prediction, rationale, forecast, retrieval note and harness-captured retrieval log. Candidate log references to external sources were inspected as evidence; I did not repeat their web or CourtListener lookups.

For each alias, reconstructed the prediction-era committed statistical artifact using:

- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000296/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000296/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000296/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

Each returned run `20261015T142602Z`, build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, landed `2026-10-13T15:28:20-04:00`, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, and `alternative_sha: null`. These commands consult statpack history only; no candidate identity history was consulted. Read the reconstructed JSON's prior-Term sal-v4 baseline segments and relevant Markdown tables to check candidates' historical statistical references. No independent scored anchor is supplied.

No corpus query/open-events, CourtListener MCP lookup, external web search, or opinion/order retrieval was performed by this evaluator. No ranged-corpus transfer lines were produced.
