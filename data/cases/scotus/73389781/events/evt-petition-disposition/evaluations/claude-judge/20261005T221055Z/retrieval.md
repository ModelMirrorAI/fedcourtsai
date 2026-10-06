# Retrieval log — claude-judge, scotus/73389781, evt-petition-disposition, run 20261005T221055Z

## Provisioned inputs

`AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; the event's `event.yaml` and `outcome.json`; `record/context.json`, `record/snapshots/2026-10-05.json` (header and proceedings), `record/documents/documents.json`, `record/documents/questions-presented.txt`; and for each of `codex-baseline`, `claude-baseline`, and `gemini-baseline` under `record/blinded/`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`. `record/opinion/` is absent, as expected on a cert cell. The committed `metrics/statpack.md` sal-v4 salience-band table (lines 187–203) was read for the segment base rate, and the same pool was cross-checked against `metrics/statpack.json`'s unrounded per-Term rates. `config/tracking.yaml`'s lookback setting and the scoring definitions in `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py` were read to match the in-code formulas. One prior committed claude-judge evaluation on another docket was read from git history for output format only.

## Corpus (`fedcourts query` / `open-events`)

None. No corpus rows were retrieved and no `ranged corpus reads` line was produced; the denial's date and shape were taken from the provisioned 2026-10-05 snapshot and `outcome.json`.

## CourtListener MCP

None.

## Web

None.
