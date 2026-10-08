# Retrieval log — claude-judge, run 20261007T150255Z

No retrieval beyond the provisioned inputs.

Read only the provisioned cell: `event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/documents.json` and `questions-presented.txt`, and every file under `record/blinded/candidate-{a,b,c}/`. Base rates were read from the committed `metrics/statpack.md` sal-v4 band table (and cross-checked against the unrounded fields in the committed `metrics/statpack.json`). No `fedcourts query` or `open-events` call, so no `ranged corpus reads` line; no CourtListener MCP call; no web search. `record/opinion/` is absent, as expected on a cert cell.
