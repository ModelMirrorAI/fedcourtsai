# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `record/documents/petition.txt`,
`record/documents/questions-presented.txt`, `record/documents/documents.json`,
`event.yaml`) and the committed `metrics/statpack.md`:

1. Corpus priors query:

   ```
   uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5
   ```

   stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`

   Returned five recency-ranked recent SCOTUS denials (three of them interim
   applications), none closely analogous to this petition; it did not move the
   estimate.

No CourtListener MCP lookups and no web searches — the provisioned record is a
complete picture of a one-entry docket, and nothing external bears on a pro se
state family-law petition at arrival.
