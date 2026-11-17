# Retrieval Log

## 1. Corpus CLI (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "578 U.S. 212" --citation "583 U.S. 202" --citation "598 U.S. 264" --limit 10`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (`note:` explained only 195 SCOTUS rows carry own parallel citations).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Result: 10 recent 2020s granted SCOTUS rows, including CVSG grant prior `scotus/73280982` (*Robinhood Markets, Inc. v. Sodha*, No. 25-944, `cvsg_date: "2026-06-01"`, `distribution_count: 3`).
3. `uv run fedcourts query --court scotus --party "Iran" --limit 15`
   - Transfer: none (CLI argument error, exit code 2: `No such option: --party`).
4. `uv run fedcourts query --court scotus --attorney "Ian Heath Gershengorn" --attorney "Carter G. Phillips" --attorney "Stuart H. Singer" --limit 15`
   - Transfer: none (CLI argument error, exit code 2: `No such option: --attorney`).
5. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (cached locally)
   - Result: 10 recent 2020s denied SCOTUS rows.
6. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (cached locally)
   - Result: 5 recent 2020s GVR SCOTUS rows, including CVSG GVR prior `scotus/73278467` (*Roybal v. Griffith*, No. 25-442, `cvsg_date: "2026-06-30"`, `distribution_count: 3`).
7. `uv run fedcourts query --court scotus --docket-number 26-293 --include-open`
   - Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: 1 open row (`scotus/9026000293`, *Kathleen Ashton, et al. v. The Taliban, et al.*, `cvsg_date: "2026-11-16"`, `distribution_count: 2`).
8. `uv run fedcourts query --court scotus --docket-number 26-294 --include-open`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (cached locally)
   - Result: 1 open row (`scotus/9026000294`, *James Owens, et al. v. The Taliban, et al.*, `cvsg_date: "2026-11-16"`, `distribution_count: 2`).

*(Also ran `uv run fedcourts paths --court "scotus" --docket "9026000292" --event "evt-order-cvsg-disposition" --role predictor` and `uv run fedcourts query --help` to inspect path bindings and CLI options.)*

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="152 F.4th 339", fields=[...])` → 0 results (F.4th reporter citation not yet indexed on the cluster).
2. `mcp_courtlistener_search(type="o", citation="170 F.4th 100", fields=[...])` → 0 results (F.4th reporter citation not yet indexed on the cluster).
3. `mcp_courtlistener_search(type="o", court="ca2", case_name="Havlish", fields=[...])` → 4 results, locating the Second Circuit en banc opinion (`cluster_id: 10811059`, `opinion_id: 11277807`, filed `2026-03-19`) and panel opinion (`cluster_id: 10660852`, `opinion_id: 11127439`, filed `2025-08-26`).
4. `mcp_courtlistener_call_endpoint(endpoint_id="clusters", query={"docket": 67110483, "fields": [...]})` → 0 results (opinions linked to sibling consolidated Second Circuit docket rather than `67110483`).
5. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[4,5,6,7,8,9,10], chunk_size=8000)` → read FSIA and TRIA sections of the Second Circuit panel opinion (*Havlish v. Taliban*).
6. `mcp_courtlistener_read_document(opinion_id=11277807)` → read the March 19, 2026 Second Circuit en banc denial order, Judge Nardini's concurrence, Judge Sullivan's dissent, and Judge Menashi's dissent (first part).
7. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[11,12,13,14,15,16,17,18,19], chunk_size=8000)` → read the panel majority's TRIA "blocking-date" holding (truncated in `petition.txt`) and Judge Sullivan's panel dissent.
8. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[5,6,7,8,9,10], chunk_size=8000)` → read Parts II and III of Judge Menashi's en banc dissent and Judges Cabranes and Calabresi's joint statement.
9. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[19], chunk_size=8000)` → read conclusion of Judge Sullivan's panel dissent.
10. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2023-01-01", q=""Foreign Sovereign Immunities Act" OR "Terrorism Risk Insurance Act"", fields=[...])` → 7 results (*CC/Devas*, *Exxon Mobil Corp. v. Corporación Cimex*, *Fuld*, *Hungary v. Simon*, *Turkiye Halk Bankasi*).
11. `mcp_courtlistener_search(type="o", court="ca11", q=""Stansell" "Revolutionary Armed Forces" "120 F.4th" OR "blocking"", fields=[...])` → 24 results, locating Eleventh Circuit *Stansell* opinions (`771 F.3d 713`, `120 F.4th 754`).
12. `mcp_courtlistener_search(type="o", court="scotus", docket_number="24-699", fields=[...])` → 1 result (*Exxon Mobil Corp. v. Corporación Cimex, S.A.*, `opinion_id: 11346053`, decided `2026-06-23`).
13. `mcp_courtlistener_search(type="o", court="ca11", citation="120 F.4th 754", fields=[...])` → 1 result (*Stansell v. Lopez Bello*, `opinion_id: 10629558`).
14. `mcp_courtlistener_search(type="o", court="ca11", citation="771 F.3d 713", fields=[...])` → 1 result (*Stansell v. Revolutionary Armed Forces of Colombia (FARC)*, `opinion_id: 2742884`).
15. `mcp_courtlistener_read_document(opinion_id=11346053, chunk_index=[0], chunk_size=8000)` → read syllabus of *Exxon Mobil Corp. v. Corporación Cimex, S.A.*
16. `mcp_courtlistener_read_document(opinion_id=10629558, chunk_index=[0,1,2,3,4], chunk_size=8000)` → read *Stansell v. Lopez Bello* (`120 F.4th 754`) to evaluate petitioners' Eleventh Circuit split argument.
17. `mcp_courtlistener_search(type="o", court="ca11", citation="45 F.4th 1340", fields=[...])` → 0 results.
18. `mcp_courtlistener_search_document(opinion_id=2742884, query="is actually an agency")` → 1 match in *Stansell I* (`771 F.3d 713`) confirming its scope.
19. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0,1,2,3,4], chunk_size=8000)` → read Judge Nardini's concurrence, Judge Sullivan's en banc dissent, and Part I of Judge Menashi's en banc dissent (including footnotes quoting the U.S. Government's 2022 Statement of Interest and 2023 Letter).
20. `mcp_courtlistener_search_document(opinion_id=11127439, query="Statement of Interest")` → 0 matches.
21. `mcp_courtlistener_search_document(opinion_id=11127439, query="United States filed")` → 0 matches.
22. `mcp_courtlistener_search_document(opinion_id=11127439, query="Exec. Order")` → 3 matches (Executive Orders 13,268, 13,224, 14,064, and 13,599).
23. `mcp_courtlistener_search(type="o", citation="657 F. Supp. 3d 311", fields=[...])` → 0 results.

## 3. Web Searches

None attempted or used.
