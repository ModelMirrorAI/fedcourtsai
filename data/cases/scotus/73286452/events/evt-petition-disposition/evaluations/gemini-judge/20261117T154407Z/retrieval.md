# Evaluator retrieval log

- Consulted committed `metrics/statpack.md` for current statpack structure and scope headers.
- Reconstructed the historical statpack build in force at the candidates' prediction run (`20260918T174135Z`) via `uv run fedcourts statpack-at`:
  - `uv run fedcourts statpack-at data/cases/scotus/73286452/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` -> `build_sha: 73762050f49cd68912e89c864e25a792e498b45a` (`sha256:345aff2a4fcdad755e6606d092e6c2475966c0bd858d291155914ef722d88fe8`, `alternative_sha: null`)
  - `uv run fedcourts statpack-at data/cases/scotus/73286452/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` -> `build_sha: 73762050f49cd68912e89c864e25a792e498b45a`
  - `uv run fedcourts statpack-at data/cases/scotus/73286452/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` -> `build_sha: 73762050f49cd68912e89c864e25a792e498b45a`
- No `fedcourts query` or `fedcourts open-events` corpus lookups, no CourtListener MCP calls, and no web searches were performed.
