No external case-fact retrieval; no corpus query/open-events, CourtListener MCP lookup, or web search was performed. Case facts were assessed only from the provisioned outcome, docket snapshot, documents, and blinded candidate artifacts.

Historical statpack verification (not case-fact retrieval):

- `uv run --no-sync fedcourts statpack-at data/cases/scotus/73377829/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` failed at uv cache initialization because the default cache was read-only; no statpack was returned.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73377829/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` succeeded.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73377829/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` succeeded.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73377829/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` succeeded.

All reconstructions selected build `7bcde3b105cb212283905eda17b827efc188e80c`, landed `2026-10-28T13:56:30-04:00`, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`; recorded digest and alternative SHA were null. Consulted its sal-v4 per-Term reached-risk-set table and the relevant circuit/relist/amicus descriptive sections, plus the current committed statpack for context. These commands emitted no ranged corpus reads line and were not corpus lookups.

Local reads also covered the evaluation contract and schemas, the event and outcome, all three candidates' prediction/rationale/forecast/retrieval documents and captured logs, the provisioned docket snapshot and document manifest, questions presented, and selected petition/appendix and opposition passages. No absent Supreme Court opinion or writing was fetched. Output validation used the local JSON schemas.
