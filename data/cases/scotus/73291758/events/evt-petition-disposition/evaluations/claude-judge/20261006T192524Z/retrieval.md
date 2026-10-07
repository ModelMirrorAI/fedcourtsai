# Retrieval — claude-judge, scotus/73291758, evt-petition-disposition, run 20261006T192524Z

No retrieval beyond the provisioned inputs.

Read, in order: `AGENTS.md`, `.github/prompts/evaluate.md`,
`schemas/evaluation.schema.json` (plus the flags and tooling schemas); then the
event's `event.yaml` and `outcome.json`, `record/context.json`, the decided
snapshot `record/snapshots/2026-10-05.json` (to check a candidate's docket
assertion), `record/documents/documents.json` and `questions-presented.txt`,
a grep of `record/documents/petition.txt` for the forfeiture language, and each
of `record/blinded/candidate-{a,b,c}/` — `prediction.json`, `reasoning.md`,
`predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`.

Base rate: the committed `metrics/statpack.md` "Segment base rate by salience
band (sal-v4)" table, baseline band, bracketed `reached` figures pooled over
OT2017–OT2024 weighted by `n` (0.05120, n=11,580); cross-checked against the
unrounded `prefix_est_grant_rate` / `prefix_weighted_resolved` in
`metrics/statpack.json` (0.05121). Also read the pooling definition in
`src/fedcourtsai/pipeline/base_rates.py` and `pipeline/evaluate.py` to match it.

No `fedcourts query` or `open-events` call (no `ranged corpus reads` line to
record), no CourtListener MCP call, no web search. Nothing under
`data/qp-topics/` was read.
