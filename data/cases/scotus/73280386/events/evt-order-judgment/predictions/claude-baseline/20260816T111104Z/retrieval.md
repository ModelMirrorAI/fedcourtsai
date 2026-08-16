# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-16.json`, `event.yaml`,
`record/context.json`, and the provisioned documents `petition.txt`,
`brief-in-opposition.txt`, `questions-presented.txt`, `documents.json`):

- Committed base rates: `metrics/statpack.md`, "The merits docket (granted
  cases)" section — pooled the per-Term disturbed rates for grant Terms
  2017–2024 (359/515 = 69.7%).
- Corpus query (one call, zero rows returned):

  ```
  uv run fedcourts query --court scotus --citation "583 U.S. 281" --limit 5 --corpus-backend service
  ranged corpus reads: 1329 GET(s), 348389376 byte(s)
  ```

  The tool noted the citations filter is sparse (161 of 590339 scotus rows
  carry citation data) and the empty result likely reflects missing data, not
  absence of the prior.
- No CourtListener MCP lookups and no web searches. The merits briefs filed on
  the docket (petitioners' brief of July 30, 2026; three amicus briefs) were
  **not** retrieved; the forecast rests on the docket skeleton and the
  cert-stage papers.
