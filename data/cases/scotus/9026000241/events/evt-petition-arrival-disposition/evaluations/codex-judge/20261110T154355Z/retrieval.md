# Retrieval

The realized event, docket, candidate prose, and captured logs were read only from the provisioned record. No corpus query/open-events lookup, CourtListener lookup, web search, external order, or external opinion retrieval was performed by this evaluator.

Historical base-rate provenance was checked with these allowed statpack-only lookups:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000241/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000241/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000241/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All three recovered build `061c238147aa000fa108f3b389e44f43cca52e87`, digest `sha256:0d05c670da5896c5e3078e0f81cbb775a2045fc05432d8d957b929849c02f891`, with checkout-slack alternative `02dd6a20fccc232651e3e13cdea3da3066e41c5b`. Neither build was frozen in the staged prediction. Both historical builds' baseline-band prior-Term reached figures support the candidates' reported arrival anchor. These commands use statpack history only and emit no ranged-corpus-read line; none is applicable. Scratch reconstructions were not written into the repository.
