# Evaluator retrieval

Read the provisioned event, outcome, context, snapshot, petition and questions presented, and each blinded candidate's prediction, rationale, forecast, retrieval note and captured retrieval log. Also read the evaluation contract, output schemas, and committed statpack. No web search, CourtListener MCP lookup, or corpus query/open-events lookup was made.

To assess the candidates' base-rate use against their actual prediction-time build, ran these statpack-only history lookups:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000115/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000115/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000115/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

Each resolved run 20260816T111104Z to build ab6fb84c09a602f661fc4b436c922fdc8de9c7fc, landed 2026-08-15T14:36:32-04:00, digest sha256:f8abdb31530370551ced5a16ef3db2ecf512b450e040799d9ec5d03b7b9f48c4; no alternative build was reported. Read that historical statpack's relevant tables. These are local statpack-history lookups, not corpus lookups, and print no ranged-corpus-read line. No candidate identity, prediction history, or alias mapping was consulted.
