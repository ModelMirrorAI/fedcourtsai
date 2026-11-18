No corpus queries, CourtListener MCP lookups, or web searches were made by this evaluator. Case facts and forecast verification used only the provisioned outcome, docket snapshot, questions presented, petition with appendix, and blinded candidate documents and captured logs. The current committed statpack was inspected as reference context.

To check candidates against the pack available when they predicted, I ran these historical-reference reconstructions (no corpus transfer lines; these commands resolve statpack history only):

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000435/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All three succeeded and selected build `7bcde3b105cb212283905eda17b827efc188e80c`, landed `2026-10-28T13:56:30-04:00`, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`. Each reported no recorded digest and `alternative_sha: null`. I read the reconstructed Markdown and JSON to check their risk-set denominators and auxiliary cuts. These checks do not supply a separately computed scoring baseline; the harness owns that anchor.
