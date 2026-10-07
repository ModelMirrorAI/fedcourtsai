# Retrieval record — claude-judge, scotus/73302615, evt-petition-disposition, run 20261006T192524Z

No retrieval beyond the provisioned inputs and the committed repository artifacts.

- No `fedcourts query` or `open-events` call (so no `ranged corpus reads` line to report).
- No CourtListener MCP call.
- No web search.

Read, in order: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; then the event's `event.yaml` and `outcome.json`; the case-level `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/questions-presented.txt` and `documents.json`; `record/blinded/<alias>/` for all three aliases (`prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`); the sal-v4 segment base-rate table in `metrics/statpack.md` and the matching `segments` rows in `metrics/statpack.json` (to pool the elevated reached rate exactly: 484 / 2810 over Terms 2017–2024); `salience.base_rate_lookback_terms` in `config/tracking.yaml`; and `is_correct`, `brier_score`, `segment_base_rate`, `brier_skill` in `src/fedcourtsai/pipeline/evaluate.py` to match the in-code definitions. A few greps over the provisioned `petition.txt` and `brief-in-opposition.txt` checked candidate factual claims (counsel of record, pendent appellate jurisdiction, panel authorship).

`record/opinion/` is absent, as expected on a cert cell. No `data/qp-topics/` path was read.

Disclosure: a scoped `git status --short` on the event directory, run to confirm no prior evaluation output existed for this run, listed the harness-moved committed `predictions/` paths as deleted. Nothing under them was opened, and the listing maps no alias to any name; no identification was attempted or formed from it.
