# Evaluator retrieval

Read the provisioned event, outcome, blinded candidate predictions, rationales, forecast documents, retrieval notes, captured logs, and the case-level snapshot and staged filings. Read the evaluation and feedback schemas and the local Evaluation model definition for the output contract.

Consulted the committed `metrics/statpack.md` for base-rate context. Recovered the candidates' historical statpack using these commands:

- `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` initially failed because the default uv cache was on a read-only filesystem; it performed no reconstruction.
- `UV_CACHE_DIR=/tmp/fedcourts-evaluator-uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` succeeded.
- `UV_CACHE_DIR=/tmp/fedcourts-evaluator-uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` succeeded.
- `UV_CACHE_DIR=/tmp/fedcourts-evaluator-uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` succeeded.

All three resolved to build `02dd6a20fccc232651e3e13cdea3da3066e41c5b` (landed August 19, 2026), digest `sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`, with no alternative build. Read the recovered sal-v3 per-Term table and confirmed the three recovered JSON packs are byte-identical. These commands read only statpack history and emitted no ranged-corpus-read line.

No evaluator corpus query, open-events call, CourtListener MCP lookup, or web search was made. Corpus and MCP calls described in candidate logs were inspected as evidence, not re-executed.
