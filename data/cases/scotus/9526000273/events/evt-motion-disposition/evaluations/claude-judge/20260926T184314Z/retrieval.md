# Retrieval — claude-judge, scotus/9526000273, evt-motion-disposition, run 20260926T184314Z

No retrieval beyond the provisioned inputs.

Read, all from the working tree: `AGENTS.md`, `.github/prompts/evaluate.md`,
`schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`,
`schemas/agent_tooling.schema.json`, the event's `event.yaml` and
`outcome.json`, `record/context.json`, `record/snapshots/2026-09-25.json`,
`record/documents/documents.json` and `application.txt` (to check two factual
claims in a candidate's rationale), the three `record/blinded/<alias>/`
directories in full (prediction, both prose documents, `retrieval.md`,
`retrieval_log.json`), the interim-docket section of the committed
`metrics/statpack.md`, and the `is_correct` / `brier_score` definitions in
`src/fedcourtsai/pipeline/evaluate.py` to match their formulas.

No `fedcourts query` or `open-events` command was run, so there is no
`ranged corpus reads` line to record. No CourtListener MCP lookup and no web
search was made. `record/opinion/` is absent, as expected on an interim cell,
and nothing was fetched to stand in for it.
