# Evaluator retrieval

No corpus, CourtListener MCP or web lookup was performed. Case facts and forecast grading use only the provisioned event, outcome, decided docket snapshot, documents and blinded candidates. The separately provisioned appendix was used only as corroborating evidence about the decision below; no Supreme Court opinion or order was fetched.

For each alias, reconstructed the statpack available at the prediction run, using only statpack history:

- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000359/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000359/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000359/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All resolved to build `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`, landed September 26, 2026, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, with no alternative build. Read the reconstructed markdown and baseline Term records to assess each candidate's anchor method. These commands emitted no ranged-corpus-read transfer line and made no corpus query. No separate evaluator-pooled baseline was computed.

Local contract/schema inspection and output validation do not add case facts. Candidate retrieval logs were reviewed as evidence; their historical calls were not re-executed.
