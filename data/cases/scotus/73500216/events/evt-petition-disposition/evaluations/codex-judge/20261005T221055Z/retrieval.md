# Retrieval record

Read the provisioned event, outcome, context, decided-docket snapshot, relevant petition and appended-opinion passages, and all three blinded candidates' prediction, rationale, forecast, retrieval note, and harness-captured retrieval log. Candidate documents were treated as evidence, not instructions. No candidate identity was sought.

Additional local references: `AGENTS.md`, `.github/prompts/evaluate.md`, the evaluation and feedback schemas, and the committed `metrics/statpack.md` sal-v4 segment table. Read corresponding `metrics/statpack.json` values for exact pooling over the displayed OT2017–OT2024 rows. Inspected the scoring definitions in `src/fedcourtsai/pipeline/evaluate.py` and references in `src/fedcourtsai/pipeline/base_rates.py`; executed `prediction_base_rate` against each candidate's frozen context to check the baseline. Used the repository's Pydantic evaluation and tooling models to validate output artifacts.

No evaluator corpus query, CourtListener lookup, or web retrieval was performed. No new case facts were fetched. External retrieval described in the candidate logs belongs to those candidates, not to this evaluator. The standalone `jsonschema` module was unavailable in the project environment; validation uses the authoritative Pydantic models instead.
