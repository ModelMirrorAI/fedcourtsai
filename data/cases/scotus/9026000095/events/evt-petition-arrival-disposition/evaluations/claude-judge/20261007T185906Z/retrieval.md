# Retrieval log — claude-judge — scotus/9026000095 — evt-petition-arrival-disposition — run 20261007T185906Z

No retrieval beyond the provisioned inputs, with these repository reads for
scoring context:

- `metrics/statpack.md` — the "Segment base rate by salience band (sal-v4)"
  table, read to resolve the cert base rate. Heading version (sal-v4) does not
  match the candidates' frozen `salience_version` (sal-v3); the rate was
  therefore omitted on every candidate rather than computed.
- `metrics/statpack.json` — read only to confirm that sal-v3 `alt_segments`
  exist per Term and that the baseline band's risk-set figures are identical
  under sal-v3 and sal-v4 (pooled OT2017–OT2025: 5.02%, n=12,720). Not used as
  a scored baseline; recorded in `flags.json` and the evaluations for the
  maintainer.
- `docs/salience.md` (sal-v3 / sal-v4 sections) and
  `src/fedcourtsai/pipeline/base_rates.py`, `pipeline/evaluate.py` — to confirm
  the version-pin rule and the in-code `correct` / `brier_score` definitions.
- Provisioned per-case inputs: `event.yaml`, `outcome.json`,
  `record/context.json`, `record/snapshots/2026-10-05.json`,
  `record/documents/{documents.json,questions-presented.txt,petition.txt,brief-in-opposition.txt}`,
  the case summary, and each candidate's `prediction.json`, `reasoning.md`,
  `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json` under
  `record/blinded/`.

No `fedcourts query` / `open-events` calls (no `ranged corpus reads` lines to
record). No CourtListener MCP lookups. No web searches.
