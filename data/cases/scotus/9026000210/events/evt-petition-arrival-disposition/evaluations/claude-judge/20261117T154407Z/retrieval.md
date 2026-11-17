# Retrieval log

- `uv run fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` — resolved build `02dd6a20fccc` (landed 2026-08-19, digest `sha256:5b70d73d…`, `alternative_sha` null); read its `statpack.md` salience-band tables to check the candidates' federal-band pooling. All three candidates share one prediction run id, so the one build serves all three. Reads statpack history only; no `ranged corpus reads` line.

No corpus query, CourtListener MCP lookup, or web search. Everything else came from the provisioned inputs (event, outcome, `record/context.json`, the 2026-11-16 snapshot and summary, the blinded candidate directories).
