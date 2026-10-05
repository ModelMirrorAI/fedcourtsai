# Retrieval log — claude-judge, scotus/9526000447, evt-motion-disposition, run 20261003T191100Z

## Provisioned inputs

`AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; the event's `event.yaml` and `outcome.json`; `record/context.json`, `record/snapshots/2026-10-03.json`, `record/documents/documents.json`, the head of `record/documents/application.txt`; and for each of `claude-baseline` and `codex-baseline` under `record/blinded/`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`. `record/opinion/` is absent, as expected on a non-merits cell. The committed `metrics/statpack.md` interim-docket section (lines 205–241) was read to check the candidates' baseline arithmetic; nothing from it was written into `evaluation.json`.

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --include-applications --docket 9526000447 --limit 3` — refused by the CLI's usage check (`--docket` is not a `query` flag); read nothing, no `ranged corpus reads` line.
2. `uv run fedcourts query --help` — flag listing only; confirmed `query` has no per-docket lookup. No corpus read.

No corpus rows were retrieved. The denial's date and shape were taken from the provisioned 2026-10-03 snapshot and `outcome.json`.

## CourtListener MCP

None.

## Web

None.
