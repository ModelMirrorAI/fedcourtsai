# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 15`
   - Stderr transfer line: `ranged corpus reads: 43 GET(s), 11075584 byte(s)`
   - Result: Returned 15 resolved SCOTUS GVR priors from the 2020s era (including distribution counts and salience metadata).

2. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1199" --limit 5`
   - Stderr transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 0 rows (note on sparse `citations` column in `scotus` scope).

3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent SCOTUS granted priors from the 2020s era.

4. `uv run fedcourts query --court scotus --docket-number 24-1238 --full`
   - Stderr transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned the corpus row for *Shawn Montgomery v. Caribe Transport II, LLC, et al.*, No. 24-1238 (`scotus/72362630`, cert granted `2025-10-03`, merits decided `2026-05-14`, `merits_judgment: "reversed"`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Montgomery v. Caribe Transport", fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 2523 seconds.`). Fell back to corpus queries and provisioned filings per `predict.md`.

## Web Searches

- None attempted.
