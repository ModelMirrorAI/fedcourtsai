# Retrieval log — claude-judge, scotus/73500236, evt-petition-disposition, run 20261007T150255Z

## Provisioned inputs read

- `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
- `events/evt-petition-disposition/event.yaml` and `outcome.json`.
- `record/context.json`, `record/snapshots/2026-10-05.json` (proceedings list), `record/documents/documents.json`, `record/documents/questions-presented.txt`, and the first ~80 lines plus a keyword grep of `record/documents/petition.txt` for my own stakes read.
- `record/blinded/<alias>/` for `codex-baseline`, `claude-baseline`, `gemini-baseline`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`. No `record/opinion/` slot exists (cert cell; nothing expected).

## Committed base rates

- `metrics/statpack.md`, "Segment base rate by salience band (sal-v4)": `baseline` column, bracketed `reached` figures, Terms 2017–2024, pooled by `n` → 0.0512 (n = 11,580).
- `metrics/statpack.json` via `fedcourtsai.pipeline.base_rates.prediction_base_rate(context, statpack, lookback_terms=10)` with codex-baseline's frozen context → 0.05120898100172712 (identical for lookback 0, since the pack holds only 2017–2026). `fedcourtsai.pipeline.evaluate.brier_skill` used for the skill numbers. `config/tracking.yaml` read for `salience.base_rate_lookback_terms` (10).

## Corpus (`fedcourts query` / `open-events`)

None. No `ranged corpus reads` line was emitted.

## CourtListener MCP

None.

## Web searches

None.
