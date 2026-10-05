# Retrieval log — claude-judge — scotus/73392441 evt-petition-disposition — run 20261005T221055Z

No retrieval beyond the provisioned inputs.

Consulted, all committed in the working tree: `AGENTS.md`, `.github/prompts/evaluate.md`, the evaluation / flags / tooling schemas, the event's `event.yaml` and `outcome.json`, `record/context.json`, the three blinded candidate directories under `record/blinded/`, `metrics/statpack.md` (the *Segment base rate by salience band (sal-v4)* table and the *Petitions by originating court* cut) and the matching unrounded baseline segment fields in `metrics/statpack.json`, the scoring definitions in `src/fedcourtsai/pipeline/evaluate.py`, and `git log` / `git show` on the event's own `event.yaml` to confirm it carried no `stage` or `moment` field at prediction time.

No `fedcourts query` or `open-events` call (no `ranged corpus reads` line to record). No CourtListener MCP call. No web search. Nothing under `data/qp-topics/` was read. `record/opinion/` is absent, as expected on a cert cell.
