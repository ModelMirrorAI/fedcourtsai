# Retrieval Log

## 1. Local Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS dockets (cert and interim dispositions).
2. `uv run fedcourts query --court scotus --citation "497 U.S. 1" --limit 5`
   - Transfer stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned 0 rows with coverage note on sparse reporter citations in the SCOTUS slice.
3. `uv run fedcourts query --court scotus --docket-number 25A1357`
   - Transfer stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned `scotus/73500446` (*Donald J. Trump v. Cable News Network, Inc.*, No. 25A1357), the linked time-extension application granted on 2026-07-10.
4. `uv run fedcourts query --court scotus --docket-number 26-223`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/9026000223` (*Donald J. Trump v. Cable News Network, Inc.*, No. 26-223), confirming `salience_score: 0.0309`, `distribution_count: 1`, `originating_court: ca11`.
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer stderr: `ranged corpus reads: 21 GET(s), 5308416 byte(s)`
   - Result: Returned 10 granted SCOTUS dockets from the 2020s era for comparison of distribution counts, amicus counts, and salience scores.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Trump v. Cable News Network"`, `fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "status"]`, `num_results=10`)
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 5049 seconds.'}`.
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Coral Ridge Ministries Media v. Southern Poverty Law Center"`, `fields=["caseName", "court", "dateFiled", "citation", "docketNumber"]`, `num_results=5`)
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 5048 seconds.'}`.

## 3. Web Searches

None attempted.
