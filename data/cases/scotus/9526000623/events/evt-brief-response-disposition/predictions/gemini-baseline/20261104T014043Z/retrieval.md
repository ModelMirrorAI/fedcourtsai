# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-6013`
   - `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - Returned the companion certiorari petition row `scotus/9026006013` (*Jesse Guardado v. Florida*, No. 26-6013, filed 2026-10-30, originating from Supreme Court of Florida No. SC2026-1605).
2. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Returned 10 recent resolved OT2026 SCOTUS dockets (primarily substantive stay applications and cert petitions).
3. `uv run fedcourts query --court scotus --docket-number 26A415`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9526000415` (*Curtis W. Beasley v. Richard Comerford, Secretary, Florida Department of Corrections*, No. 26A415, capital stay application filed 2026-09-28, response filed 2026-09-28, referred to the Court and denied 2026-09-29).
4. `uv run fedcourts query --court scotus --docket-number 26A311`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/9526000311` (*William George Davis v. Texas*, No. 26A311, capital extension application).
5. `uv run fedcourts query --court scotus --docket-number 26A200`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/9526000200` (*Elieser Sori Rodriguez v. United States*, No. 26A200, extension application).
6. `uv run fedcourts query --court scotus --party "Florida" --era 2020s --limit 20`
   - Rejected with usage error (`No such option: --party`).
7. `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 25`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 25 recent resolved OT2026 SCOTUS applications.

## CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Guardado v. State"`, `num_results=10`)
   - Returned 30 results, including the decision below (*Jesse Guardado v. State of Florida*, No. SC2026-1605, filed 2026-10-29, `cluster_id=11049070`, `opinion_id=11516852`) and prior Florida Supreme Court decisions (`Guardado I`–`V`).
2. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=11049070`, `fields=["id", "case_name", "date_filed", "sub_opinions"]`)
   - Confirmed cluster metadata for `SC2026-1605` (filed 2026-10-29).
3. `mcp_courtlistener_read_document` (`opinion_id=11516852`)
   - Read the full text of the Florida Supreme Court's October 29, 2026 decision affirming the summary denial of Guardado's successive postconviction motion and denying a stay of execution.
4. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Florida"`, `filed_after="2025-01-01"`, `num_results=20`)
   - Returned 0 results.
