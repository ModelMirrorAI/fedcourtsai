# Retrieval

No corpus query, CourtListener MCP lookup, web search, or external case-fact retrieval was performed. Evaluation used the provisioned blinded candidates, staged outcome, docket, questions presented, petition appendix, prompt, and schemas.

To check the candidates' historical base-rate use without reading prediction identities, reconstructed the statpack for each staged alias:

- `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

The first invocation failed because the default uv cache was read-only. The three invocations with the temporary cache succeeded without package installation. Each selected build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, landed October 13, 2026, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, with no alternative build. Read the reconstructed JSON to check sal-v4 state risk-set pooling for Terms 2017–2025. These commands consult statpack-only repository history, not candidate prediction history. They print no ranged-corpus transfer line; no ranged corpus reads were made.
