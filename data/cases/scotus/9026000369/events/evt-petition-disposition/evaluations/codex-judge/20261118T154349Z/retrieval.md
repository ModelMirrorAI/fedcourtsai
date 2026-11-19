Read the provisioned event, outcome, blinded candidate documents and captured logs, resolved docket snapshot, petition, questions presented, appendix, document manifest, and context. Consulted the evaluation/tooling/flags schemas and current `metrics/statpack.md` locally. No corpus query, CourtListener MCP lookup, or web search was performed by this evaluator.

To check historical base-rate context without identifying any candidate, ran:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All three commands succeeded and reconstructed build `648fc43559f5480348a438523a81df100b5c7301` (landed `2026-10-30T20:13:49-04:00`), digest `sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`, matching each candidate's frozen `cert_anchor`. Each reported `alternative_sha: null`. These local statpack-history reads produced no `ranged corpus reads` line. Historical marginal tables and sal-v4 per-Term context were read from the recovered pack; no baseline was independently pooled.

Candidate-reported retrieval is evidence assessed in their evaluations, not retrieval performed by this evaluator. Local Python/jsonschema checks validate only this cell's output files.
