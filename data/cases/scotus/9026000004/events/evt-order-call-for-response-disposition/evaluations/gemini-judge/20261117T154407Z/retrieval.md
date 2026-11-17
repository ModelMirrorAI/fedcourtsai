# Evaluator Retrieval Log

- **Case / Event:** `scotus/9026000004` / `evt-order-call-for-response-disposition`
- **Evaluator / Run:** `gemini-judge` / `20261117T154407Z`

## Historical statpack reconstruction (`fedcourts statpack-at`)

No `fedcourts query` / `open-events` corpus lookups, CourtListener MCP calls, or web searches were executed. To verify the candidates' base-rate citations against the statpack in force at prediction run `20261029T180303Z` rather than only the current committed `metrics/statpack.md` (`sal-v8`), I reconstructed the run-time statpack via `fedcourts statpack-at`:

- `uv run fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` (and into the project scratch directory `/home/runner/.gemini/tmp/fedcourtsai/statpack-at/{gemini-baseline,claude-baseline,codex-baseline}` for `read_file` inspection) → resolved `build_sha: 7bcde3b105cb212283905eda17b827efc188e80c` (`landed_at: 2026-10-28T13:56:30-04:00`, `digest: sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `alternative_sha: null`, `sal-v4`) identically across all three candidates.
