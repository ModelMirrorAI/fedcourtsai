# Retrieval log — claude-judge, 20260930T201759Z

No retrieval beyond the provisioned inputs and the committed repository.

- No `fedcourts query` or `fedcourts open-events` call was made (no `ranged corpus reads` line to record).
- No CourtListener MCP call was made.
- No web search was made.
- Read from the committed tree: `metrics/statpack.md` (the interim docket section, to state the pool the harness stamp will draw on) and `src/fedcourtsai/pipeline/evaluate.py` (the `is_correct` and `brier_score` definitions, to match them).
- Read from the cell: `event.yaml`, `outcome.json`, `record/context.json`, `record/documents/documents.json`, `record/snapshots/2026-09-29.json`, and every file under `record/blinded/candidate-{a,b,c}/`. Nothing under `data/qp-topics/` was read.
