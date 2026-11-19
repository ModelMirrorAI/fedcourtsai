No corpus queries, CourtListener MCP lookups, or web searches were made by this evaluator. Case facts were graded solely from the provisioned outcome, blinded candidates, docket snapshot, and filings.

Historical base-rate context was reconstructed with these permitted, statpack-only history lookups:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73538544/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73538544/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73538544/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All three succeeded and selected build `7bcde3b105cb212283905eda17b827efc188e80c`, landed `2026-10-28T13:56:30-04:00`, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, with no recorded candidate digest and no alternative build. The reconstructed Markdown and JSON supplied the prediction-time sal-v4 and relist tables. These commands emit no `ranged corpus reads` line because they do not query the corpus. No prediction history was accessed.
