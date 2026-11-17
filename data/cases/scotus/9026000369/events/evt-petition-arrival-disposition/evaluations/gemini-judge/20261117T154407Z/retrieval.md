# Retrieval log

- Reconstructed the statpack build in force at candidate run time (`20260927T182226Z`) using `uv run fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for `claude-baseline`, `codex-baseline`, and `gemini-baseline` (`build_sha`: `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`, `digest`: `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, `sal-v4`).
- No `fedcourts query` or `fedcourts open-events` corpus lookups, no CourtListener MCP lookups, and no web searches were performed beyond the provisioned inputs and local statpack git history.
