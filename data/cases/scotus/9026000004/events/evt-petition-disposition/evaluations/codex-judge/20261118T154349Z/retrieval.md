No retrieval beyond the provisioned inputs.

Reconstructed the prediction-time statpack using the contract-authorized local statpack-history helper for each blinded alias:

- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three resolved to build `7bcde3b105cb212283905eda17b827efc188e80c`, landed October 28, 2026, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, with no alternative build. These commands consult only statpack history and emit no ranged-corpus-read line. No corpus query, CourtListener lookup or web search was performed by this evaluator.
