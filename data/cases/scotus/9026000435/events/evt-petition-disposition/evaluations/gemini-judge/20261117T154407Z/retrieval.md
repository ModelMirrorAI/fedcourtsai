No corpus queries (`fedcourts query` / `open-events`), CourtListener MCP lookups, or web searches were performed beyond the provisioned repository inputs.

Historical statpack reconstruction performed per `.github/prompts/evaluate.md` to verify candidate base-rate claims against the build in force at prediction time:
- `uv run fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for `codex-baseline`, `gemini-baseline`, and `claude-baseline` → resolved `build_sha: 7bcde3b105cb212283905eda17b827efc188e80c` (`digest: sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `alternative_sha: null`).
