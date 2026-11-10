# Retrieval Log (`scotus/9026000351`, `evt-petition-arrival-disposition`, `gemini-judge`, `20261110T154355Z`)

- Rebuilt the statpack in force at the candidates' prediction run (`20260927T182226Z`) using `uv run fedcourts statpack-at`:
  - `uv run fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` -> `build_sha: 2420d5dd72e1dd97585b5f0c998b82f40c3b5a32` (`digest: sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`)
  - `uv run fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` -> `build_sha: 2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`
  - `uv run fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` -> `build_sha: 2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`
- No `fedcourts query` / `open-events` corpus lookups, CourtListener MCP calls, or web searches were performed beyond the provisioned inputs and `statpack-at`.
