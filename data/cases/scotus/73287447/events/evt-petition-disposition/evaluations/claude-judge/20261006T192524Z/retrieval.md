# Retrieval log — claude-judge, scotus/73287447, evt-petition-disposition

No retrieval beyond the provisioned inputs. No `fedcourts query` / `open-events` corpus lookups (so no `ranged corpus reads` lines), no CourtListener MCP calls, no web searches.

Committed repository files read for the grade, besides the cell's own inputs (`event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/*`, and the three `record/blinded/<alias>/` directories): `metrics/statpack.md` (the sal-v4 segment base rate table, for the pooled `elevated` reached rate), `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, `src/fedcourtsai/pipeline/evaluate.py` (to match the in-code definitions), and the committed case summary `summaries/2026-10-05.md`.
