# Retrieval log — claude-judge, scotus/73358839, evt-petition-disposition, run 20261005T221055Z

Provisioned inputs read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, the event's `event.yaml` and `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json` (docket entries through the 2026-10-05 denial), and for each of `record/blinded/codex-baseline|b|c/`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`. `record/opinion/` is absent, as expected on a cert cell. Also read `metrics/statpack.md` (the sal-v4 "Segment base rate by salience band" table and its caption), `src/fedcourtsai/pipeline/evaluate.py` (the `is_correct`, `brier_score`, `segment_base_rate`, `brier_skill` definitions, to match them) and `config/tracking.yaml` (the ten-Term lookback).

## Corpus tooling

- `uv run fedcourts open-events --court scotus --docket 73281689` — the companion petition (No. 25-1201, docket 73281689) still lists `evt-petition-disposition` as open in the corpus the cell's service reads. Context only; no case fact was taken from it into any grade. `open-events` prints no `ranged corpus reads` line.
- `uv run fedcourts query --court scotus --docket 73281689` — refused: `query` carries no per-docket flag; the call printed the help text and read nothing. No transfer line.
- `uv run fedcourts corpus-info` — failed inside the cell (the corpus blob is not on the cell's disk; the cell reads through the service), so I cannot quote a corpus vintage for the companion-open observation above. It is stated as a service read of unknown vintage.

## CourtListener MCP

None.

## Web

None.

Nothing under `data/qp-topics/` was read. The committed `predictions/` and `evaluations/` trees were not read; `git status` shows them deleted, which is the harness's blinding move, and I did not restore anything.
