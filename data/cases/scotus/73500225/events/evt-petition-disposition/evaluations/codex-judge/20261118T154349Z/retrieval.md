No external case-fact retrieval, corpus query/open-events lookup, CourtListener MCP lookup, or web search was performed. Case facts came from the provisioned outcome, blinded candidate documents and captured logs, docket snapshot, and filings. The current committed statpack and output schemas were read locally.

To assess each candidate against the statpack available when it ran, I reconstructed only statpack history through the contract-authorized command. Each command returned build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, landed September 28, 2026, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, with no alternative build. The scratch outputs are outside the repository. No ranged-corpus transfer line was produced.

- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv uv run --no-sync fedcourts statpack-at data/cases/scotus/73500225/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv uv run --no-sync fedcourts statpack-at data/cases/scotus/73500225/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv uv run --no-sync fedcourts statpack-at data/cases/scotus/73500225/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

Read the reconstructed sal-v4 band and relist/CVSG tables to check the candidates' baseline methodology. No new case facts or opinion bodies were fetched. The candidates' historical searches discussed in the evaluations are their captured activity, not evaluator retrieval.
