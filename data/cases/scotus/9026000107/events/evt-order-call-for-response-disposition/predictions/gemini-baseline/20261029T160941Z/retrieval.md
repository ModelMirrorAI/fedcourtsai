# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-107 --decided-before 2026-09-03`
   - Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned the masked pre-cutoff corpus row for `scotus/9026000107` (`Garnell Walls v. Prince George's County, Maryland, et al.`).

2. `uv run fedcourts query --court scotus --citation "594 U.S. 474" --citation "588 U.S. 180" --decided-before 2026-09-03 --limit 10`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Empty result (sparse `citations` column coverage note).

3. `uv run fedcourts query --court scotus --docket-number 26-15 --decided-before 2026-09-03`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/9026000015` (*Gary Perez, et al. v. City of San Antonio, Texas*).

4. `uv run fedcourts query --court scotus --docket-number 26-107`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned the live forward-mode corpus row for `scotus/9026000107` (`distributed_for_conference: 2026-11-06`, `distribution_count: 2`, `last_live_polled: 2026-10-29`, unresolved).

5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 28 GET(s), 7143424 byte(s)`
   - Result: Returned 10 recent granted SCOTUS priors from the 2020s era.

6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent denied SCOTUS priors from the 2020s era.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Tedford's Tenancy", filed_before="2026-09-03")`
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 7925 seconds.'}`

2. `mcp_courtlistener_search(type="o", case_name="Walls v. Prince George's County", filed_before="2026-09-03")`
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 7925 seconds.'}`

## Web Searches

- None attempted.
