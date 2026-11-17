# Evaluator Retrieval Log

- Read committed `metrics/statpack.md` (`sal-v8`) and ran `uv run fedcourts statpack-at data/cases/scotus/9026000440/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for `claude-baseline`, `gemini-baseline`, and `codex-baseline` to reconstruct the statpack build in force at `20261030T011325Z` (`build_sha: 7bcde3b105cb212283905eda17b827efc188e80c`, `digest: sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `sal-v4`).
- Ran `uv run fedcourts paths --court scotus --docket 9026000440 --event evt-petition-disposition --role evaluator` to verify cell paths.
- No `fedcourts query` or `fedcourts open-events` calls, no CourtListener MCP lookups, and no web searches.
