# Retrieval log — claude-judge, run 20261007T185906Z

## Provisioned and committed inputs read

- `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
- `events/evt-petition-disposition/event.yaml` and `outcome.json`; `record/context.json`; `record/documents/documents.json`, `questions-presented.txt`, the opening pages of `petition.txt`, and the table of contents and reasons sections of `brief-in-opposition.txt`; `record/snapshots/2026-10-05.json` (proceedings list); `summaries/2026-10-05.md`.
- `record/blinded/candidate-{a,b,c}/`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md` (context only, unscored), `retrieval.md`, `retrieval_log.json`.
- `metrics/statpack.md`: the sal-v4 "Segment base rate by salience band" table (pooled the `baseline` bracketed `reached` figures over OT2017–OT2025), and, to verify candidates' citations, the relist-count, CVSG-status, and originating-court tables.
- `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py`, to confirm the in-code pooling (resolved-weighted mean of per-Term rates, version-pinned, Terms strictly before the case's) matches the hand pooling.

## Corpus lookups

None. No `fedcourts query` or `open-events` calls; no `ranged corpus reads` lines.

## CourtListener MCP lookups

None.

## Web searches

None.
