# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS priors for general baseline context.

2. `uv run fedcourts query --court scotus --citation "596 U.S. 767" --citation "591 U.S. 464" --citation "607 U.S. 492" --limit 10`
   - Stderr: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: Returned coverage note that `--citation` matches a case's own parallel cites on the 200 populated SCOTUS rows.

3. `uv run fedcourts query --court ca1 --judge "Gelpí" --judge "Thompson" --judge "Montecalvo" --limit 10`
   - Stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
   - Result: 0 rows returned (circuit judge lists are withheld on the circuit slice).

4. `uv run fedcourts query --court scotus --docket-number "25-77"`
   - Stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned `scotus/73272830` (*Stephen Foote, et al. v. Ludlow School Committee, et al.*, No. 25-77, originating from `ca1`, cited in the First Circuit's opinion below; certiorari denied 2026-04-20 after 13 distributions).

5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 22 GET(s), 5570560 byte(s)`
   - Result: Returned 10 recent granted SCOTUS cases from the 2020s era.

## CourtListener MCP Calls

1. `mcp_courtlistener_search(court="ca1", docket_number="25-1417", type="o", fields=["caseName", "dateFiled", "citation", "judge", "absolute_url"])`
   - Result: Error HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 7503 seconds.`). Degraded gracefully to provisioned `record/documents/appendix.txt` (which contains the full First Circuit and District Court opinions) and corpus tooling.

## Web Searches

- None attempted.
