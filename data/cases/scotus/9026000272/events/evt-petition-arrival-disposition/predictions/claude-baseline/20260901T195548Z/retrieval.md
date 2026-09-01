# Retrieval log

Beyond the provisioned inputs (snapshot, `record/context.json`,
`record/documents/petition.txt`, `record/documents/questions-presented.txt`,
`documents.json`) and the committed `metrics/statpack.md`:

- `uv run fedcourts query --court scotus --citation "605 U.S. 495" --limit 3`
  — `ranged corpus reads: 1346 GET(s), 352452608 byte(s)` — 0 rows; the CLI
  printed its citation-coverage note (159 of 590604 scotus rows carry
  citation data), so the empty result reflects the sparse column, not a
  missing prior.
- `uv run fedcourts query --court scotus --citation "475 U.S. 503" --limit 3`
  — `ranged corpus reads: 1341 GET(s), 351141888 byte(s)` — 0 rows, same
  coverage note.

No CourtListener MCP lookups. No web searches.
