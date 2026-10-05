# Retrieval log (evaluator)

No retrieval beyond the provisioned inputs. Read for this cell: the event's
`event.yaml` and `outcome.json`, the case-level `record/` (context, snapshot,
documents, and the three blinded candidates with their retrieval logs), the
committed `metrics/statpack.md` band table (sal-v4) for the base rate, and the
code definitions in `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py`
to match the pooling. No `fedcourts query` / `open-events`, no CourtListener
MCP call, and no web search was made, so there is no `ranged corpus reads` line
to report.
