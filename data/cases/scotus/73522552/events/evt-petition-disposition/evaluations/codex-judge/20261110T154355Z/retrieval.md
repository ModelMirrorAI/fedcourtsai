# Evaluator retrieval

Read only the evaluation contract, output schemas, this case's provisioned event/outcome, blinded candidate files and captured logs, questions presented, selected petition/opposition passages, and the November 9 docket snapshot for case facts. No corpus query, open-events, CourtListener MCP lookup, or web search was performed by this evaluator. No opinion body or separate writings were staged.

For historical base-rate context, ran these blind-safe statpack-history lookups:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73522552/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73522552/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73522552/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

Each resolved prediction run `20261006T142731Z` to build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, landed September 28, 2026, with digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, no recorded candidate digest, and no alternative build. Read the recovered gemini-baseline sal-v4 per-Term table; all three resolved to identical builds. These commands report no ranged-corpus-read transfer line. Historical pack inspection was limited to checking candidates' anchoring methods, not pooling or quoting an evaluator baseline.

Local validation uses the committed JSON schemas and installed Python validation tooling. No packages were installed and no identity-bearing prediction history was read.
