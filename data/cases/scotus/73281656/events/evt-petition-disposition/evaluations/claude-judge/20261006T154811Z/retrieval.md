# Retrieval log

No retrieval beyond the provisioned inputs. Specifically:

- Read, in order: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; then the cell's `event.yaml`, `outcome.json`, `record/context.json`, the decided snapshot `record/snapshots/2026-10-05.json`, `record/documents/questions-presented.txt` and `documents.json`, and the committed case summary `summaries/2026-10-05.md` (context only).
- Read every file under `record/blinded/claude-baseline`, `codex-baseline`, `gemini-baseline`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`.
- Read `metrics/statpack.md`, section "Segment base rate by salience band (sal-v4)", for the pooled baseline.
- No `fedcourts query` or `open-events` call, so no `ranged corpus reads` line to report. No CourtListener MCP lookup. No web search. `record/opinion/` is absent, as expected on a cert cell.
