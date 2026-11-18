No corpus queries, open-events calls, CourtListener MCP lookups, or web searches were made by this evaluator. Case facts were checked only against the provisioned outcome, docket snapshot, questions presented, petition appendix, and blinded candidate files. The case record contains no staged opinion or separate-writing texts. I also read the evaluation/tooling schemas and the committed statpack.

To assess candidates' quoted base-rate figures against their original build, I ran the following permitted statpack-history reconstructions (no case or prediction history was consulted):

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All succeeded and selected build `7bcde3b105cb212283905eda17b827efc188e80c`, landed `2026-10-28T13:56:30-04:00`, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, with `alternative_sha: null`. I read the reconstructed pack's relevant tables and fields. These are local history operations, not corpus lookups, so no `ranged corpus reads` line was emitted. Candidate-reported lookups were reviewed as evidence of their retrieval, not repeated as evaluator lookups.
