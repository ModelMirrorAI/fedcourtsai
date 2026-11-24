# Retrieval Log

All lookups attempted beyond the provisioned files in `data/cases/scotus/9026000078/record/` are listed below (no web searches were used, and no lookups targeted the disposition or third-party forecasts of this case):

## Corpus CLI (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000078" --event "evt-petition-disposition" --role predictor && uv run fedcourts query --help`
   - Transfer: none (path check and CLI flag help).
2. `uv run fedcourts query --court scotus --docket-number 25-6623`
   - Stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: 1 row (`scotus/73282277`, *Hamed Kian v. Florida*, No. 25-6623, `disposition: "granted"`, `date_cert_granted: "2026-06-15"`, cited in the petition and reply brief).
3. `uv run fedcourts query --court scotus --docket-number 26-76`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 1 row (`scotus/9026000076`, companion petition *Michael James Jackson v. Florida*, No. 26-76, open/pending, `distributed_for_conference: "2026-12-11"`, `distribution_count: 3`).
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15`
   - Stderr: `ranged corpus reads: 41 GET(s), 10616832 byte(s)`
   - Result: 15 resolved 2020s granted SCOTUS cert rows (distribution/CVSG/counsel patterns on recent grants).
5. `uv run fedcourts query --court scotus --attorney "Jeffrey L. Fisher" --era 2020s --limit 20`
   - Result: CLI error (`No such option: --attorney`), 0 corpus reads.
6. `uv run fedcourts query --court scotus --party "Florida" --era 2020s --disposition granted --limit 15`
   - Result: CLI error (`No such option: --party`), 0 corpus reads.
7. `uv run fedcourts query --court scotus --party "Florida" --era 2020s --disposition denied --limit 15`
   - Result: CLI error (`No such option: --party`), 0 corpus reads.
8. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 10 resolved 2020s denied SCOTUS rows (including Florida capital petition *Thomas M. Overton v. Florida, et al.*, `scotus/9026006154`).
9. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 10 resolved 2020s GVR SCOTUS rows.

## CourtListener MCP

1. `mcp_courtlistener_search` (`type="o"`, `court="fla"`, `case_name="Jackson v. State"`, `filed_after="2025-12-01"`, `filed_before="2026-01-15"`, `fields=["caseName","citation","dateFiled","docketNumber","cluster_id","opinions"]`)
   - Result: `query_id: 53b5bdd3`, `count: 2`; located *Michael James Jackson v. State of Florida*, No. SC2023-1298 (Fla. Dec. 18, 2025), `opinion_id: 11228303` (the decision below in companion petition No. 26-76, relied upon by the Florida Supreme Court in *Hunt*).
2. `mcp_courtlistener_search` (`type="o"`, `case_name="State v. Lobato"`, `filed_after="2024-01-01"`, `fields=["caseName","citation","dateFiled","court_id","cluster_id","opinions"]`)
   - Result: `query_id: b7f8a7d5`, `count: 3`; located *State of Florida v. Angel Alejandro Lobato*, No. 6D23-3201 (Fla. 6th DCA May 31, 2024), `opinion_id: 9975949`.
3. `mcp_courtlistener_read_document` (`opinion_id=11228303`, `chunk_index=[0, 6, 7]`, `chunk_size=8000`)
   - Result: Read chunks 0, 6, and 7 of *Michael James Jackson v. State of Florida* (`total_chars: 118603`), confirming Jackson's 2005 offense date (explaining why *Jackson* lacks *Hunt*'s Ex Post Facto claim) and 8-4 jury recommendation.
4. `mcp_courtlistener_read_document` (`opinion_id=11228303`, `chunk_index=[2, 3, 4, 5, 14]`, `chunk_size=8000`)
   - Result: Read chunks 2–5 and 14 of *Michael James Jackson v. State of Florida* (Sixth/Eighth Amendment analysis and Justice Labarga's concurring-in-result opinion).
5. `mcp_courtlistener_search` (`type="o"`, `case_name="Kian v. State"`, `fields=["caseName","citation","dateFiled","docketNumber","cluster_id","opinions"]`)
   - Result: `query_id: a7e04b0c`, `count: 2`; located *Hamed Kian v. State of Florida*, No. 4D2024-2370 (Fla. 4th DCA Oct. 16, 2025), `opinion_id: 11219338`.
6. `mcp_courtlistener_search` (`type="d"`, `docket_number="25-6623"`, `fields=["caseName","docketNumber","dateFiled","docket_id"]`)
   - Result: Failed with MCP error (`fetch failed`).
7. `mcp_courtlistener_read_document` (`opinion_id=11219338`)
   - Result: Read full text (`1055` chars) of *Hamed Kian v. State of Florida* per curiam affirmance, confirming its non-capital Fourth DCA origin.

## Web Search

None attempted.
