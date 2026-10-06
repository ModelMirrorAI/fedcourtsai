# Retrieval record — claude-judge, scotus/73281635, evt-petition-disposition, run 20261006T154811Z

## Provisioned and committed inputs read

- `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
- `events/evt-petition-disposition/event.yaml` and `outcome.json`; `record/context.json`; `record/snapshots/2026-10-05.json` (proceedings list only, to confirm the disposition date and the pre-prediction docket state); `record/documents/documents.json`, `questions-presented.txt`, and targeted greps of `petition.txt` and `brief-in-opposition.txt` to verify the candidates' factual claims (verdict and interest amounts, the April 2024 agreement, the split framing, the apportionment remand, the BIO's structure and counsel, the Seventh Circuit panel and citation).
- `record/blinded/candidate-{a,b,c}/`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`. No `record/opinion/` slot was staged (cert cell; nothing to grade semantically).
- `metrics/statpack.md`, "Segment base rate by salience band (sal-v4)" table, for the pooled prior-Term `elevated` reached rate.
- `src/fedcourtsai/pipeline/base_rates.py` and `evaluate.py`, to confirm the pooling definition; ran `prediction_base_rate` over the committed `metrics/statpack.json` as a cross-check (0.1722 unrounded vs 0.1724 from the rendered percentages).

## Corpus lookups

None. No `fedcourts query` or `open-events` call was made, so no `ranged corpus reads` line was emitted.

## CourtListener MCP

None.

## Web searches

None.
