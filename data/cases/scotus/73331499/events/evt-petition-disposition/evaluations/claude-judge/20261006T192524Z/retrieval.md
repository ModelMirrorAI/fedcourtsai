# Retrieval log — claude-judge, scotus/73331499, evt-petition-disposition, run 20261006T192524Z

No retrieval beyond the provisioned inputs.

Read locally only: `AGENTS.md`, `.github/prompts/evaluate.md`, the three output schemas, the event's `event.yaml` and `outcome.json`, the case-level `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/questions-presented.txt` and `documents.json`, a grep of `record/documents/petition.txt`, the three `record/blinded/<alias>/` directories (prediction, both prose documents, `retrieval.md`, `retrieval_log.json`), the sal-v4 segment table in `metrics/statpack.md`, and the scoring definitions in `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py`.

No `fedcourts query` / `open-events` call (so no `ranged corpus reads` line), no CourtListener MCP call, no web search. `record/opinion/` is absent, as expected on a cert cell.
