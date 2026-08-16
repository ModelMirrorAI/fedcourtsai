# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-16.json`, `event.yaml`,
`record/context.json`, and the provisioned document texts —
`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`):

- **Committed statpack** (`metrics/statpack.md`) — "The merits docket (granted
  cases)" section, for the pooled strictly-prior disturbed-rate baseline
  (grant Terms 2017–2024, 359/515 = 69.7%).
- **Corpus query** (one call, via the cell's corpus service):

  ```
  uv run fedcourts query --court scotus --citation "415 U.S. 361" --corpus-backend service
  ```

  stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`

  Returned no rows, with the tool's own note that the citations filter is
  sparse (161 of 590,339 rows in scope carry citation data) and matches a
  case's own reporter cites only — a coverage gap, not "no such precedent".
  Not retried.

- **CourtListener MCP:** not used.
- **Web searches:** none.
