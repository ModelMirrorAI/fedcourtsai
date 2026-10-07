# Retrieval log — claude-judge, run 20261007T185906Z

No corpus query (`fedcourts query` / `open-events`), no CourtListener MCP call,
and no web search. Beyond the provisioned inputs (`event.yaml`, `outcome.json`,
`record/context.json`, the 2026-10-05 snapshot, `record/documents/` including
the brief in opposition, and the three blinded candidates' staged files), I
read only committed repository material:

- `metrics/statpack.md` — the "Segment base rate by salience band" table
  (heading sal-v4) and its caption, to check the version against each
  prediction's frozen `context.salience_version` (sal-v3).
- `metrics/statpack.json` — to confirm which salience versions the pack
  carries (sal-v1 through sal-v4) and to pool the sal-v3 baseline-band
  `reached` figures for the reader's note in each `evaluation.md`; no number
  from it was written into any `evaluation.json`.
- `src/fedcourtsai/pipeline/evaluate.py` and `pipeline/base_rates.py` — the
  in-code definitions of `is_correct`, `brier_score`, `brier_skill`, and the
  version-pinned pooling, to match them.
- `schemas/evaluation.schema.json`, `agent_flags.schema.json`,
  `agent_tooling.schema.json` — the output contracts.

The `record/opinion/` slot is absent, as expected on a cert cell. No
`ranged corpus reads` line to record, since no corpus command ran.
