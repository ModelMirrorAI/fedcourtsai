# Evaluation retrieval

Read the evaluation contract and schemas, the provisioned event and outcome, the staged case snapshot/context and document materials, and all three blinded candidates' prediction, rationale, forecast and retrieval files. No web search, CourtListener MCP lookup, fedcourts query or fedcourts open-events call was made by this evaluator. References to candidate retrieval in the evaluations describe their staged logs, not new evaluator lookups.

Consulted the committed metrics statpack and reconstructed historical statpacks using these commands (UV_CACHE_DIR=/tmp/uv-cache for each):

- `uv run --no-sync fedcourts statpack-at data/cases/scotus/73548979/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `uv run --no-sync fedcourts statpack-at data/cases/scotus/73548979/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run --no-sync fedcourts statpack-at data/cases/scotus/73548979/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

Each resolved build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, landed October 13, 2026, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, with no recorded candidate digest and no alternative build. Only statpack history was consulted; no candidate identity or prediction history was accessed. The commands emitted no ranged-corpus-reads line because they reconstruct committed reference material, not corpus query results. Local arithmetic verified the strictly-prior elevated reached pool as 484/2,810. Scratch artifacts remain outside the repository.
