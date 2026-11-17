# Retrieval log — `scotus/9026000435`, `evt-petition-arrival-disposition`, `gemini-judge`, run `20261117T154407Z`

## Local statpack reconstruction beyond the provisioned case inputs

- Read `metrics/statpack.md` (committed checkout).
- Reconstructed the statpack build in force at the candidates' prediction run (`20261001T215439Z`) via:
  - `uv run fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
  - `uv run fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - `uv run fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
  - Resolved build for all three candidates: `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5` (`digest`: `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, `landed_at`: `2026-09-28T08:12:04-04:00`, `alternative_sha`: `null`). Read `/tmp/statpack-at/codex-baseline/statpack.md` to verify the `sal-v4` segment base-rate rows (`OT2017`–`OT2025`) the candidates read.

## Corpus, CourtListener MCP, and web lookups

- Corpus queries (`fedcourts query` / `open-events`): None.
- CourtListener MCP lookups: None.
- Web searches: None.
