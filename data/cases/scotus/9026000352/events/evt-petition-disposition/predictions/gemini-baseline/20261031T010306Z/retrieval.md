# Retrieval Log (`scotus/9026000352` — `evt-petition-disposition`)

## Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --help`
   - Inspected CLI options before running structured queries (no transfer line).
2. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Stderr transfer line: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Returned 10 recent resolved 2020s SCOTUS priors (`26-2`, `26A499`, `26A535`, `26A532`, `26-346`, `26-5347`, `26A512`, `26A555`, `26A556`, `26A416`).
3. `uv run fedcourts query --court scotus --citation "601 U.S. 23" --limit 5`
   - Stderr transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned empty with coverage note (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).
4. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 5 recent resolved 2020s denied SCOTUS rows from warm service cache.

## CourtListener MCP Lookups

- None attempted (the Fourth Circuit per curiam opinion and Western District of North Carolina dismissal order were provisioned in full inside `record/documents/appendix.txt`).

## Web Searches

- None attempted.
