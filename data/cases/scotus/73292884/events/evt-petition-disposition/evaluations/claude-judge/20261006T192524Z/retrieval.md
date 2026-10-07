# Retrieval log

No retrieval beyond the provisioned inputs.

Read only the cell's own inputs: `outcome.json`, `event.yaml`, the case-level `record/` (context, the 2026-10-05 snapshot, the provisioned petition, brief in opposition, and questions presented, and the three blinded candidates with their retrieval logs), `metrics/statpack.md` / `metrics/statpack.json`, and the pipeline's base-rate pooler run offline against the committed statpack. No `fedcourts query` or `open-events` call, no CourtListener MCP lookup, no web search.
