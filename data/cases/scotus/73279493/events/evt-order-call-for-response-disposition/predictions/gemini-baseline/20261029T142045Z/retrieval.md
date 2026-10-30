# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Purpose: Inspect recent 2020s granted SCOTUS cases in the corpus.

2. `uv run fedcourts query --court scotus --docket-number "25-651"`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Purpose: Check corpus metadata for docket 25-651 (*Stanley Kappell Watson v. Shenekka Bradsher, et al.*).

3. `uv run fedcourts query --court scotus --citation "523 U.S. 57" --limit 10`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Purpose: Check whether *Kawaauhau v. Geiger*, 523 U.S. 57 (1998), appeared in the corpus citation index (returned 0 rows).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `citation="523 U.S. 57"`)
   - Result: HTTP 429 rate-limit error (shared daily quota exhausted).
2. `mcp_courtlistener_search` (`type="o"`, `court="ca11"`, `q=""Stanley Kappell Watson" OR "Sheneeka Bradsher" OR "147 F.4th 1330""`)
   - Result: HTTP 429 rate-limit error (shared daily quota exhausted).
   - Note: The full texts of the Eleventh Circuit opinion (*147 F.4th 1330*, App. A) and the lower district and bankruptcy court orders (Apps. B–E) are provisioned in `record/documents/petition.txt` and were read directly from the provisioned record.

## Web Searches

- None.
