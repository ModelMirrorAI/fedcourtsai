# Evaluator retrieval record

No corpus query, open-events call, CourtListener lookup, web search, or external case-fact retrieval was performed. Case facts and forecast checks use only the provisioned event, outcome, blinded candidate documents and captured logs, staged docket snapshot, questions presented, and appendix. No opinion or writings slot is staged; none was fetched.

I inspected the committed statpack and reconstructed the historical pack for each candidate to avoid confusing a later metrics refresh with a forecast error:

- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three selected build `7bcde3b105cb212283905eda17b827efc188e80c`, landed October 28, 2026, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, with `alternative_sha: null`. These commands inspect statpack history only and emit no ranged-corpus-read line. I checked the historical per-Term table and exact prior-Term counts locally; I did not compute a replacement scoring baseline or inspect prediction history.
