# Retrieval Log

Provisioned inputs consulted:

- `AGENTS.md`
- `.github/prompts/predict.md`
- `schemas/prediction.schema.json`
- `schemas/agent_tooling.schema.json`
- `schemas/agent_flags.schema.json`
- `data/cases/ca11/66800253/events/evt-appeal-disposition/event.yaml`
- `data/cases/ca11/66800253/record/context.json`
- `data/cases/ca11/66800253/record/snapshots/2026-07-10.json`

Additional local context consulted:

- `metrics/statpack.md`
- `metrics/statpack.json`
- `src/fedcourtsai/pipeline/outcome.py`
- `src/fedcourtsai/pipeline/ingest.py`
- `tests/test_ingest.py`
- `tests/cassettes/realistic-grant/prediction.json`
- `tests/cassettes/realistic-grant/reasoning.md`

Corpus lookup attempts:

- `UV_CACHE_DIR=/tmp/uv-cache TMPDIR=/tmp uv run fedcourts query --court ca11 --limit 10 --corpus-backend ranged`
  - Failed before returning rows because DNS/network resolution for the ranged corpus backend failed.
  - No `ranged corpus reads: ...` line was printed.
- `UV_CACHE_DIR=/tmp/uv-cache TMPDIR=/tmp uv run fedcourts stats --court ca11 --resolved-only`
  - Returned the graceful local-corpus fallback: `_No corpus present - run after dvc pull._`
  - No `ranged corpus reads: ...` line was printed because this was a local-corpus stats attempt and no local corpus was present.

No CourtListener MCP lookups or web searches were used. I did not open this
case's linked opinion clusters, docket page, or any search result for the case's
own disposition.
