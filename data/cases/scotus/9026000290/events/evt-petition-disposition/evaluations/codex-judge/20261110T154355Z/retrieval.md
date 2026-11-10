# Evaluator retrieval record

The outcome, event, resolved docket snapshot, context, petition/document manifest, questions presented, and all three candidates' blinded predictions, rationales, forecast documents, retrieval notes and harness-captured retrieval logs were read locally. No additional case facts, external order/opinion text, CourtListener MCP results or web material were retrieved.

Historical base-rate context was reconstructed through the contract-authorized statpack-only history reader, without opening prediction history or identifying candidates:

- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000290/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000290/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000290/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

Each returned build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, landed October 19, 2026, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, `recorded_digest = null`, and `alternative_sha = null`. No ranged-corpus transfer line was emitted; these were local statpack-history reconstructions, not corpus queries. The reconstructed sal-v4 band/risk-set table and contextual relist/CVSG cuts were inspected. No evaluator-specific baseline was pooled or written.

No `fedcourts query` or `open-events` call, CourtListener MCP lookup, or web search was made by this evaluator. Candidate-reported lookups discussed in their evaluations are not evaluator retrievals. Schema/tool availability and output-validation commands are administrative checks, not additional case evidence.
