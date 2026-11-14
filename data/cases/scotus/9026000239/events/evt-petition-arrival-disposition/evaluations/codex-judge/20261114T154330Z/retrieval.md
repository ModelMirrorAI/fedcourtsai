# Evaluator retrieval

Read the evaluation prompt and schemas; the resolved event and outcome; the provisioned context, docket snapshot, questions presented and relevant petition passages; and every staged candidate's prediction, rationale, forecast, retrieval note, and harness-captured retrieval log. Consulted the committed statpack header and reconstructed the historical statpack for base-rate-use review. No external case facts, opinion bodies, orders, or commentary were fetched.

## Historical statpack reconstruction

These commands consult only statpack history, not prediction history or alias mappings:

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

Each returned build `02dd6a20fccc232651e3e13cdea3da3066e41c5b`, landed August 19, 2026, digest `sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`, with no alternative build and no recorded candidate digest. Read the reconstructed sal-v3 federal-band table and its denominator definition. These commands printed no ranged-corpus-read line and did not invoke corpus query/open-events.

## Other retrieval

No evaluator corpus queries, CourtListener MCP lookups, or web searches. Candidates' historical retrievals are assessed from their staged logs, not repeated. No packages were installed.
