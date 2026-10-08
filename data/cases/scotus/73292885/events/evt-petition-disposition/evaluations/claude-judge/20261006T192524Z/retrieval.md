# Retrieval log (evaluator, claude-judge, run 20261006T192524Z)

## Provisioned inputs read

- `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
- `events/evt-petition-disposition/event.yaml` (stage `cert`), `outcome.json` (denied 2026-10-05, actual_granted 0).
- `record/blinded/candidate-{a,b,c}/` — `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json` for each alias.
- `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`. No `record/opinion/` slot was staged (cert cell, expected).
- `metrics/statpack.md`, section "Segment base rate by salience band (sal-v4)" (caption: most recent 10 of 10 Terms rendered), and `config/tracking.yaml` for `salience.base_rate_lookback_terms` (10).

## Corpus (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 73292885 --event evt-petition-disposition --role evaluator` — path resolution only; no `ranged corpus reads` line (not a query).
- No `fedcourts query` or `open-events` call.

## CourtListener MCP

1. `get_endpoint_item(endpoint_id="dockets", item_id=73292885, fields=[id, case_name, docket_number, court_id, date_filed])` — to check gemini-baseline's retrieval-note claim that this docket id resolves to a different caption. Returned `docket_number` 25-1249, `court_id` scotus, `date_filed` 2026-05-04, `case_name` "Roy J. Meidinger, Petitioner v. Commissioner of Internal Revenue". Used only for the data-quality flag; no case fact entered any grade.

## Web

No web searches.
