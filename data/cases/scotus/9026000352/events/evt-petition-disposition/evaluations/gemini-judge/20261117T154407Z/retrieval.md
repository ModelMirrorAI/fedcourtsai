# Evaluator Retrieval Log (`scotus/9026000352` — `evt-petition-disposition`)

No corpus (`fedcourts query` / `open-events`), CourtListener MCP, or web lookups were performed beyond the provisioned inputs and `metrics/statpack.md`.

## Local Statpack History Verification (`fedcourts statpack-at`)

- `uv run fedcourts statpack-at data/cases/scotus/9026000352/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
  - Resolved `build_sha`: `648fc43559f5480348a438523a81df100b5c7301` (`digest`: `sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`, `alternative_sha`: `null`).
- `uv run fedcourts statpack-at data/cases/scotus/9026000352/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - Resolved same `build_sha`: `648fc43559f5480348a438523a81df100b5c7301`.
- `uv run fedcourts statpack-at data/cases/scotus/9026000352/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
  - Resolved same `build_sha`: `648fc43559f5480348a438523a81df100b5c7301`.
