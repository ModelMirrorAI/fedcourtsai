# Retrieval log (evaluator)

## Provisioned inputs

- `event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-10-02.json`, `record/documents/documents.json` and the OCR-recovered `application.txt` (read for the application's ask and its related-proceedings list, as post-decision context for `reasoning_quality` and `big_case`).
- `record/blinded/<alias>/` for codex-baseline, claude-baseline, gemini-baseline: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`.
- `metrics/statpack.md`, section "The interim docket (applications)", to read what the harness will pool for the stamped baseline (Terms 2025 and 2024 strictly before application-Term 2026).
- `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; `src/fedcourtsai/pipeline/evaluate.py` for the `is_correct` and `brier_score` definitions.
- No `record/opinion/` slot is staged (interim cell; nothing expected).

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --include-open --include-applications --era 2020s --limit 400`, filtered client-side to the applicant's name and docket numbers 26-153 / 26A434 / 26A397 / 26A331, to check claude-baseline's claims about the applicant's prior applications. Returned 26A434 (substantive, denied 2026-10-01), 26A397 (substantive, denied 2026-09-23, no response, no referral) and 26A331 (extension, granted 2026-09-11). `ranged corpus reads: 18 GET(s), 4718592 byte(s)`.

## CourtListener MCP

None.

## Web

None.
