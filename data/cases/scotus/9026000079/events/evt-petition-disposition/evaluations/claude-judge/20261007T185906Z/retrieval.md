# Retrieval log (evaluator)

No retrieval beyond the provisioned inputs. Consulted only in-repo, committed material:

- `metrics/statpack.md` — the sal-v4 "Segment base rate by salience band" table (bracketed `baseline` `reached` figures, Terms 2017–2025, pooled resolved-weighted: 0.0501 over n = 12,720) and the relist-count and CVSG cuts, read for context on the candidates' anchoring.
- `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json` — output contract.
- `src/fedcourtsai/pipeline/evaluate.py` — to match the in-code `is_correct` / `brier_score` / `brier_skill` definitions.

No `fedcourts query` / `open-events` calls (so no `ranged corpus reads` lines), no CourtListener MCP calls, no web searches or fetches.
