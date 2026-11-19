No external case-fact retrieval, corpus query, CourtListener MCP lookup, or web search was performed by this evaluator. Read the provisioned event, outcome, blinded candidate documents and captured logs, record/context.json, record/documents/, and November 16 docket snapshot. Also read the output schemas and relevant committed statpack context.

To verify the candidates' historical base-rate use, ran these local archival reconstructions (environment: UV_CACHE_DIR=/tmp/evaluate-uv-cache UV_NO_SYNC=1 UV_OFFLINE=1):

- `uv run fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All three succeeded and selected build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, landed September 28, 2026, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, with no alternative build. Inspected that build's sal-v4 segment table and distribution/CVSG context. These are local statpack-history operations, not corpus lookups, and emit no `ranged corpus reads` line. No candidate identity or prediction history was consulted.
