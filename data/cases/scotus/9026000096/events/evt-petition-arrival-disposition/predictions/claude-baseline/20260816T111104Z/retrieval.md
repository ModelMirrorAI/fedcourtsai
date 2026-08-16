# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `record/documents/questions-presented.txt`,
`record/documents/petition.txt`, `record/documents/documents.json`, and
`event.yaml`):

- Committed base rates: `metrics/statpack.md` — "Segment base rate by salience
  band (sal-v3)" (the `federal` column, Terms 2017–2025), "Modern
  discretionary-cert petitions by disposition", the relist-count and
  CVSG-status cuts, and the per-Term table.
- Corpus lookup:
  `uv run fedcourts query --court scotus --citation '590 U.S. 604' --citation '529 U.S. 728' --citation '446 U.S. 500'`
  (the petition's public-lands grant lineage — Cowpasture, Babbitt, Andrus).
  Returned no rows. stderr:
  `ranged corpus reads: 1329 GET(s), 348389376 byte(s)` and a coverage note
  that only 161 of 590,339 scotus rows carry citation data (missing data, not
  no match). Not retried per the sparse-filter guidance.
- No CourtListener MCP lookups and no web searches: the cell is forward-mode
  with retrieval unrestricted, but the provisioned petition text, docket
  snapshot, and statpack covered every signal the forecast uses, and further
  searching risked surfacing nothing this arrival-moment record needs.
