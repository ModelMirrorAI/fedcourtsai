# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. **Companion docket lookup (`No. 26-193`, *Hall v. Fleming*):**
   - Command: `uv run fedcourts query --court scotus --docket-number 26-193 --decided-before 2026-10-06`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned 1 row (`scotus/9026000193`, *Bethany M. Hall v. A. Scott Fleming, Director, Virginia State Counsel of Higher Education*, docket `26-193`, filed `2026-08-14`, originating from `ca4` docket `25-1574`, unresolved as of `2026-10-06`).

2. **Recent 2020s SCOTUS resolved priors before cutoff:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --decided-before 2026-10-06 --limit 10`
   - Transfer line: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Result: Returned 10 resolved SCOTUS rows decided on or before `2026-10-05` (including denials and GVRs from the Long Conference order list).

3. **Reporter citation lookup for *Hall v. Fleming* (`175 F.4th 510`):**
   - Command: `uv run fedcourts query --citation "175 F.4th 510" --decided-before 2026-10-06`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 0 rows (with coverage note that only 200 rows in scope carry reporter citations).

4. **Recent 2020s SCOTUS granted priors before cutoff:**
   - Command: `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-10-06 --limit 10`
   - Transfer line: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
   - Result: Returned 10 granted SCOTUS rows resolved on or before `2026-10-01`.

## 2. CourtListener MCP Calls

1. **Opinion search for *Hall v. Fleming*:**
   - Tool: `mcp_courtlistener_search` (`type="o"`, `case_name="Hall v. Fleming"`, `filed_before="2026-10-06"`, `fields=["id","cluster_id","caseName","court","dateFiled","citation","status"]`)
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 12481 seconds.`).

2. **Docket search for *Johnson v. Fleming*:**
   - Tool: `mcp_courtlistener_search` (`type="d"`, `case_name="Johnson v. Fleming"`, `filed_before="2026-10-06"`, `fields=["id","docket_id","caseName","court","dateFiled","docketNumber"]`)
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 12481 seconds.`).

## 3. Web Searches
- None attempted.
