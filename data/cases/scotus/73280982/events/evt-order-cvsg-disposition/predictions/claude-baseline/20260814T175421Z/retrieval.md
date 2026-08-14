# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-14, `petition.txt`,
`brief-in-opposition.txt`, `questions-presented.txt`, `documents.json`,
`record/context.json`) and the committed `metrics/statpack.md`:

- `uv run fedcourts query --court scotus --citation "601 U.S. 257" --limit 3`
  — known-case lookup for Macquarie Infrastructure v. Moab Partners; returned
  **no rows** (the citation column is sparse: the tool noted 161 of 590,020
  scotus-scope rows carry citation data).
  stderr: `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`
- One malformed `fedcourts query` invocation (free-text argument, rejected by
  the CLI before any corpus read) and one `--help` call; no corpus transfer.

No CourtListener MCP lookups. No web searches.
