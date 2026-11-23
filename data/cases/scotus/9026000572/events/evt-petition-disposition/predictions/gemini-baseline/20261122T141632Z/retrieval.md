# Retrieval Log

Mode: `forward` (no retrieval cutoff; strictly avoided querying this case's own disposition or any external forecasts).

## `fedcourts` Corpus Queries

1. `uv run fedcourts query --court scotus --docket-number 26-104`
   - Stderr: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: 1 row (`scotus/9026000104`, *Philip L. Rhoney, Acting Director of the Buffalo Field Office of U.S. Immigration and Customs Enforcement v. Ricardo Aparecido Barbosa da Cunha*, `date_filed: 2026-07-23`, `distributed_for_conference: 2026-09-28`, `distribution_count: 1`, `date_cert_granted: 2026-10-01`, `disposition: "granted"`). Confirmed lead vehicle grant and shared counsel (D. John Sauer for petitioner; Michael King Thomas Tan and Matthew Hyrum Adams for respondent).

2. `uv run fedcourts query --court scotus --docket-number 25-1415`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 1 row (`scotus/73529868`, *Matthew Putra, Director of the Detroit Field Office of U.S. Immigration and Customs Enforcement v. Juan Manuel Lopez-Campos*, `date_filed: 2026-06-24`, `distributed_for_conference: 2026-09-28`, `distribution_count: 1`, `disposition: null`). Confirmed companion Sixth Circuit SG petition is being held since the September 28, 2026 Conference without weekly relisting.

3. `uv run fedcourts query --court scotus --docket-number 26-43`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 1 row (`scotus/9026000043`, *Victor Buenrostro-Mendez, et al. v. Todd Blanche, Attorney General, et al.*, `date_filed: 2026-07-10`, `distributed_for_conference: 2026-09-28`, `distribution_count: 1`, `disposition: null`). Confirmed companion Fifth Circuit alien petition is likewise being held since the September 28, 2026 Conference.

4. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 15` and `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 15`
   - Stderr: `ranged corpus reads: 44 GET(s), 11403264 byte(s)` (combined shell invocation; second command served from cached pages)
   - Result: 15 recent 2020s SCOTUS `gvr` rows and 15 recent `denied` rows from October–November 2026 conferences, confirming `distribution_count` patterns (`>= 2` on held/relisted GVRs, `1` only where intervening precedent predated initial distribution).

5. `uv run fedcourts query --court scotus --disposition gvr --decided-before 2026 --era 2020s --limit 25` and `uv run fedcourts query --court scotus --disposition denied --decided-before 2026 --era 2020s --limit 25`
   - Stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)` (combined shell invocation)
   - Result: 25 pre-OT2026 `gvr` rows and 25 `denied` rows, including June 2026 end-of-Term cleanup GVRs (e.g., Nos. 25-79, 25-372, 25-1027, 25-1042), all carrying `distribution_count >= 2` upon post-merits redistribution.

6. `uv run fedcourts query --court scotus --party "Immigration and Customs Enforcement" --era 2020s --limit 20`
   - Result: Failed (`Exit Code: 2`, `No such option: --party` — CLI does not expose a `--party` filter).

7. `uv run fedcourts query --court scotus --disposition denied --decided-before 2026-07-02 --era 2020s --limit 25`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 25 SCOTUS denial rows resolved before `2026-07-02`, including June 29–30, 2026 end-of-Term cleanup denials of held SG petitions (*United States v. Daniels*, No. 24-1248, `distribution_count: 4`; *United States v. Sam*, No. 24-1249, `distribution_count: 4`; *Trump v. O. Doe*, No. 25-899, `distribution_count: 2`), confirming that held petitions denied after an affirmance in the lead case are redistributed (`distribution_count >= 2`) for the cleanup conference and then denied.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `citation="175 F.4th 61"`, `fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"]`)
   - Result: 0 results (`query_id="0b4464a1"` — reporter citation not yet indexed).

2. `mcp_courtlistener_search` (`type="o"`, `citation="166 F.4th 494"`, `fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"]`)
   - Result: 0 results (`query_id="26a5630c"`).

3. `mcp_courtlistener_search` (`type="o"`, `citation="170 F.4th 1128"`, `fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"]`)
   - Result: 0 results (`query_id="e21cb013"`).

4. `mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `case_name="Barbosa da Cunha"`, `fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"]`)
   - Result: 1 result (`query_id="2d5683ba"`, `cluster_id=10983473`, `opinion_id=11451136`, *Barbosa Da Cunha v. Freden*, filed `2026-09-25`, order denying rehearing en banc).

5. `mcp_courtlistener_search` (`type="o"`, `court="ca5"`, `case_name="Buenrostro-Mendez"`, `fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"]`)
   - Result: 0 results (`query_id="d7d7277a"`).

6. `mcp_courtlistener_read_document` (`opinion_id=11451136`, `chunk_index=0`, `chunk_size=12000`)
   - Result: Error `"No text is available for this document."`

7. `mcp_courtlistener_call_endpoint` (`endpoint_id="dockets"`, `query={"court": "scotus", "docket_number": "26-104", "fields": ["id", "case_name", "date_filed", "date_argued", "date_terminated"]}`)
   - Result: 1 result (`query_id="188e8ae0"`, `id=75102765`, *Philip L. Rhoney ... v. Ricardo Aparecido Barbosa da Cunha*, `date_filed="2026-07-23"`, `date_argued=null`, `date_terminated=null`), confirming the lead granted case has not yet been argued or decided.

## Web Searches
- None.
