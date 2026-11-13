# Retrieval Log

Mode: `forward` (`scotus/9026000594`, `evt-petition-arrival-disposition`). No web searches (`google_web_search` or `web_fetch`) were attempted. All retrieval beyond the provisioned inputs used `uv run fedcourts query` (corpus priors) and the CourtListener MCP server (lower-court and prior Supreme Court opinions).

## 1. Corpus CLI (`fedcourts`) Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000594" --event "evt-petition-arrival-disposition" --role predictor` (plus `uv run fedcourts query --help`)
   - Resolved cell paths and CLI flags (no corpus transfer).
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15`
   - `ranged corpus reads: 42 GET(s), 10944512 byte(s)`
   - Returned 15 recent resolved 2020s SCOTUS granted petitions and substantive applications (through November 9, 2026).
3. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 15`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 15 recent resolved 2020s SCOTUS GVR dispositions (through November 9, 2026).
4. `uv run fedcourts query --court scotus --citation "604 U.S. 650" --citation "602 U.S. 367" --limit 10`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows (`note:` sparse reporter-citation coverage on live rows).
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 60`
   - `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
   - Returned the 60 most recent granted SCOTUS matters (through November 9, 2026), confirming no merits-docket Tucker Act grant-termination vehicle had yet been granted and showing recent Solicitor General grant patterns.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="Sustainability Institute v. Trump", num_results=5)`
   - Returned 1 result: *The Sustainability Institute v. Donald Trump*, No. 25-1575 (4th Cir. Jan. 21, 2026) (`cluster_id=10778864`, `opinion_id=11245474`).
2. `mcp_courtlistener_search(type="o", case_name="Solutions in Hometown Connections v. Noem", num_results=5)`
   - Returned 1 result: *Solutions in Hometown Connections v. Kristi Noem*, No. 25-1384 (4th Cir. Jan. 23, 2026) (`cluster_id=10779193`).
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="American Public Health Association", num_results=5)`
   - Returned 0 results under that caption string.
4. `mcp_courtlistener_search(type="o", court="scotus", q='"Tucker Act"', filed_after="2025-01-01", num_results=20)`
   - Returned 4 SCOTUS clusters, including *Department of Education v. California*, 604 U.S. 650 (Apr. 4, 2025, `24A910`, `cluster_id=10373019`), and *National Institutes of Health v. American Public Health Ass'n* (Aug. 21, 2025, `25A103`).
5. `mcp_courtlistener_search(type="o", q='"Dep't of Educ. v. California" OR "Department of Education v. California" "Tucker Act"', filed_after="2025-08-01", num_results=20)`
   - Returned 274 lower-court matches (20 shown), including *Thakur v. Trump* (9th Cir. May 26, 2026, `cluster_id=10864473`), *Commonwealth of Mass. v. NIH* (1st Cir. Jan. 5, 2026, `cluster_id=10769055`), *State of New York v. Trump* (1st Cir.), and *Sustainability Institute v. Trump* (4th Cir.).
6. `mcp_courtlistener_search_document(opinion_id=11245474, query="Climate United")`
   - Searched Fourth Circuit opinion in *Sustainability Institute v. Trump*; 0 literal matches for `"Climate United"`.
7. `mcp_courtlistener_search(type="d", court="scotus", q='"Sustainability Institute" OR "Thakur" OR "Hometown Connections" OR "Global Health Council" OR "Commonwealth of Massachusetts"', filed_after="2025-06-01", num_results=20)`
   - Returned 0 RECAP docket results (SCOTUS docket coverage on CourtListener RECAP is sparse).
8. `mcp_courtlistener_search(type="o", court="scotus", case_name="Geo Group v. Menocal", num_results=5)`
   - Returned 1 result: *Geo Group, Inc. v. Menocal*, No. 24-758 (decided Feb. 25, 2026, `cluster_id=10800194`).
9. `mcp_courtlistener_read_document(opinion_id=11245474, chunk_index=0, chunk_size=6000)`
   - Read opening 6,000 characters of *The Sustainability Institute v. Donald Trump* (4th Cir. Jan. 21, 2026), confirming the Fourth Circuit's Tucker Act holding on IRA/IIJA environmental grants.
10. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10864473)`
    - Retrieved cluster metadata for *Thakur v. Trump* (`date_filed="2026-05-26"`, sub-opinions `11331696`, `11331917`).
11. `mcp_courtlistener_read_document(opinion_id=11331696, chunk_index=0, chunk_size=4000)`
    - Returned `"No text is available for this document."`
12. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10769055)`
    - Retrieved cluster metadata for *Commonwealth of Mass. v. National Institutes of Health* (`date_filed="2026-01-05"`, sub-opinion `11235640`).
13. `mcp_courtlistener_search(type="o", court="scotus", q='"Department of Education v. California"', filed_after="2025-04-05", num_results=10)`
    - Returned 3 SCOTUS opinion clusters citing *Department of Education v. California* (*NIH v. American Public Health Ass'n*, *Trump v. Boyle*, *A.A.R.P. v. Trump*).
