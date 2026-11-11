# Evaluator retrieval

Read the evaluation contract, output schemas, and provisioned event, outcome, context, docket snapshot, petition/QP text, and every blinded candidate's prediction, rationale, forecast, retrieval note, and captured retrieval log. No live corpus query, open-events call, CourtListener lookup, or web retrieval was used.

Historical base-rate provenance was checked with these permitted statpack-only history lookups:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000290/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000290/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000290/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All recovered build 2420d5dd72e1dd97585b5f0c998b82f40c3b5a32, digest sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c, landed September 26, 2026, with no alternative build. Read the recovered statpack's scope and sal-v4 prior-Term risk-set table to evaluate historical anchor use, not to supply an independent scored baseline. These commands are not corpus queries and emitted no ranged-corpus-read line.
