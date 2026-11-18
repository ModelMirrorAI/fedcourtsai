No corpus query, CourtListener lookup, or web search was performed by this evaluator. Case facts and forecast assessments use only the provisioned event, outcome, blinded candidates, docket snapshot and document texts. The opinion/writings slot is absent.

Read the committed `metrics/statpack.md` for statistical context. To assess the candidates against their contemporaneous build rather than today's sal-v8 pack, ran these local historical-statpack reconstructions (statpack history only; no prediction history):

- Initial command: `UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`. It exited 2 before execution because the default uv cache was read-only.
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`.
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`.
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`.

All three successful reconstructions selected build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, landed `2026-10-13T15:28:20-04:00`, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, with `alternative_sha: null`. Read the recovered sal-v4 markdown table and JSON baseline reached fields and checked codex-baseline's reported arithmetic locally. These commands produced no `ranged corpus reads` line; they are not corpus lookups.

Candidate retrieval logs were read as grading evidence. Their searches and reported corpus transfers are the candidates' activity, not this evaluator's retrieval.
