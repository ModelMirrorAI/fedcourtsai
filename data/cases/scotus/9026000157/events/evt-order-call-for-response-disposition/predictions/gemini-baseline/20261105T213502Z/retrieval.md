# Retrieval Log

## 1. Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000157" --event "evt-order-call-for-response-disposition" --role predictor`
   - Purpose: Resolve cell paths for `scotus/9026000157`.
   - Output: Returned `case_id`, `corpus`, and `event` path.

2. `uv run fedcourts query --help`
   - Purpose: Check structured filter options for `fedcourts query`.

3. `uv run fedcourts query --court scotus --docket-number 25-849 --limit 5`
   - Transfer line: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Purpose: Inspect prior church-autonomy / neutral-principles petition cited in `petition.txt` (*United States Conference of Catholic Bishops v. David O'Connell*, No. 25-849).
   - Result: Returned 1 row (`scotus/73280351`), confirming that No. 25-849 was distributed 4 times, drew 14+ amicus briefs (including briefs from two of the same amici appearing in No. 26-157), and was denied certiorari on `2026-05-26`.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(court="scotus", case_name="Lutheran Church", type="d")`
   - Purpose: Check whether a cert petition had been docketed on CourtListener from *Lutheran Church—Missouri Synod v. Christian*, 178 F.4th 193 (5th Cir. 2026).
   - Result: `0` results.

2. `mcp_courtlistener_search(court="scotus", case_name="McRaney", type="d")`
   - Purpose: Check whether a cert petition had been docketed on CourtListener from *McRaney v. North American Mission Board of the Southern Baptist Convention*, 157 F.4th 627 (5th Cir. 2025).
   - Result: `0` results.
