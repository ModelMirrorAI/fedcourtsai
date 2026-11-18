# Retrieval record

Reviewed the provisioned event, outcome, docket snapshot, petition and appendix excerpts, questions presented, and all three blinded candidates' predictions, rationales, forecasts, retrieval notes, and harness-captured logs. Consulted the output schemas and committed statpack for context.

Historical statpack recovery (statpack history only, no prediction history):

- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000526/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000526/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000526/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All succeeded and selected build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, landed October 19, 2026, with no alternative build. Read its sal-v4 table and JSON to check the candidates' historical base-rate use. These commands read local artifact history, not the remote corpus; no ranged-corpus transfer lines were emitted.

No evaluator corpus queries, CourtListener MCP lookups, web searches, or external case-fact retrieval were performed. Searches and lookups described inside candidate logs were reviewed as evidence, not reissued.
