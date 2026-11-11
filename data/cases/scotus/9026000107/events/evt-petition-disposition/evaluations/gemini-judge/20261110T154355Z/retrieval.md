# Retrieval log

- Reconstructed the statpack build in force at the candidates' prediction run time (`20261005T231540Z`) for `claude-baseline`, `codex-baseline`, and `gemini-baseline`:
  - `uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
  - `uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
  - `uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - Resolved build: `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5` (`sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, landed `2026-09-28T08:12:04-04:00`).
- No `fedcourts query` or `fedcourts open-events` corpus lookups, CourtListener MCP calls, or web searches were performed beyond the provisioned inputs and `statpack-at`.
