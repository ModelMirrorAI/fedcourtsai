No corpus queries (`fedcourts query` / `open-events`), CourtListener MCP lookups, or web searches were performed.

- Reconstructed the candidates' prediction-time statpack build from local git history via `uv run fedcourts statpack-at data/cases/scotus/73500225/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for `claude-baseline`, `gemini-baseline`, and `codex-baseline` (resolved to `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`).
