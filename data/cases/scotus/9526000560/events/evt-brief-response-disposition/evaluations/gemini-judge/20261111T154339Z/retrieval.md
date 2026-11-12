# Retrieval Log

- `uv run fedcourts statpack-at data/cases/scotus/9526000560/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` (and for `gemini-baseline`, `claude-baseline`): reconstructed the statpack build (`7bcde3b105cb212283905eda17b827efc188e80c`, landed `2026-10-28T13:56:30-04:00`) in force at the candidates' prediction run (`20261029T212853Z`) to verify their interim base-rate figures.
- No `fedcourts query` / `open-events` corpus lookups, no CourtListener MCP calls, and no web searches were performed beyond the provisioned inputs and `statpack-at`.
