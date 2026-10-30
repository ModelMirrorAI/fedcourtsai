# Retrieval log

Corpus lookups:
- `uv run fedcourts query --court scotus --docket-number 23-199` returned this
  petitioner's prior petition (Anibowei v. Mayorkas), denied 2024-01-08.
  stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
- `uv run fedcourts query --court scotus --docket-number 20-1043` returned
  United States v. Cano, denied 2021-06-28.
  stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
- `uv run fedcourts query --court scotus --citation "573 U.S. 373" --limit 3`
  returned no rows. It printed a note that the citations column is sparse.
  stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

Committed base rates: `metrics/statpack.md` (the band table and the relist,
CVSG and amicus cuts).

No CourtListener MCP calls and no web searches.
