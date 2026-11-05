# Retrieval log

- `uv run fedcourts query --court scotus --citation "577 U.S. 385" --limit 3`:
  `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. No rows; note says the citation column is sparse.
- `uv run fedcourts query --court scotus --citation "565 U.S. 73" --limit 3`:
  `ranged corpus reads: 0 GET(s), 0 byte(s)`. No rows; same note.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`:
  usage error (unknown era 'modern'). No transfer line.
- `uv run fedcourts query --court scotus --docket-number 20-7311`:
  `ranged corpus reads: 694 GET(s), 181731328 byte(s)`. Returned the petitioner's 2021 prior cert
  petition row (Louisiana origin), with sparse fields.
- `uv run fedcourts query --help`: usage only.
- Read `metrics/statpack.md` (band, relist, CVSG, amicus, by-Term sections).
- No CourtListener MCP calls and no web searches.
