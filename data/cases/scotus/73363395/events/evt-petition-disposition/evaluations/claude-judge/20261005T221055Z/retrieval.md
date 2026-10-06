# Retrieval log — claude-judge, scotus/73363395 evt-petition-disposition, run 20261005T221055Z

## Provisioned and committed inputs read

- `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
- `events/evt-petition-disposition/event.yaml` and `outcome.json`; case-level `record/context.json`, `record/snapshots/2026-10-05.json` (proceedings list), `record/documents/documents.json`, `questions-presented.txt`, and grep/sed excerpts of `petition.txt` to check the candidates' quotations (Seventh Amendment passages, "only binding upon federal courts", In re 1978 Chevrolet Van in the table of authorities, the Reasons for Granting section); `summaries/2026-09-27.md`.
- `record/blinded/candidate-{a,b,c}/`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`.
- `record/opinion/` is absent (cert cell; nothing expected).
- `metrics/statpack.md` (header, "Segment base rate by salience band (sal-v4)", "Cert petitions by relist count", "Modern cert petitions by originating circuit") and `metrics/statpack.json` (`terms[].segments` for the `baseline` band, to pool the bracketed `reached` rate at full precision: 593 / 11,580 over Terms 2017–2024).
- `src/fedcourtsai/pipeline/evaluate.py` (`is_correct`, `brier_score`, `brier_skill`, `segment_base_rate`) to match the in-code definitions, and `src/fedcourtsai/serialize.py` / `fedcourtsai.schemas` to write and validate the outputs.

## Corpus lookups

None. No `fedcourts query` or `open-events` call was made, so there is no `ranged corpus reads:` line to report.

## CourtListener MCP lookups

None.

## Web searches

None.
