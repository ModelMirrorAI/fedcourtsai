# Retrieval record — claude-judge, scotus/73281376, evt-petition-disposition

No retrieval beyond the provisioned inputs.

For transparency, the committed files consulted beyond the event's own directory, none of which is retrieval:
`metrics/statpack.md` (the sal-v4 segment table) and `metrics/statpack.json` (its unrounded `prefix_est_grant_rate`
/ `prefix_weighted_resolved` fields, used to pool the elevated band over Terms 2017–2024); the case-level
`record/documents/` texts (questions presented, petition with appendix, brief in opposition) and the 2026-10-05
snapshot, read to check candidates' characterisations of the Fourth Circuit opinion and the brief in opposition;
`src/fedcourtsai/pipeline/base_rates.py` and `evaluate.py` to match the pooling and skill definitions. No
`fedcourts query` or `open-events` call, no CourtListener MCP call, no web search, and nothing under
`data/qp-topics/`.
