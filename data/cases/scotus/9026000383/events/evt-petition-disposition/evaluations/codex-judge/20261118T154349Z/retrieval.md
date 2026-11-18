# Retrieval

Read the evaluation prompt and schemas, provisioned event/outcome, all three blinded predictions and prose documents, their harness-captured retrieval logs, the case snapshot, context, petition, appendix, document manifest, and questions presented. Consulted the committed statpack for base-rate context.

Recovered each candidate's original statpack using only the authorized statpack-history command:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000383/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000383/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000383/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three calls succeeded and selected build `648fc43559f5480348a438523a81df100b5c7301`, digest `sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`, with `alternative_sha: null`. Read relevant historical tables from `/tmp/statpack-at/gemini-baseline/statpack.md`; all three candidates were pinned to that same build. These local-history commands printed no `ranged corpus reads` line.

No evaluator corpus query/open-events call, CourtListener lookup, or web search was made. Candidates' retrievals are assessed in their evaluations and are not evaluator lookups. No new case facts or external order/opinion text were retrieved. Output validation is local JSON Schema validation.
