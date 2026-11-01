# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts`)
1. `uv run fedcourts paths --court "scotus" --docket "9026000516" --event "evt-petition-disposition" --role predictor`
   - Resolved cell paths (`case_id scotus/9026000516`).
2. `uv run fedcourts query --help`
   - Inspected CLI options and filter vocabulary.
3. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
   - Returned 10 recent OT2026/2020s SCOTUS GVR dispositions (`scotus/73317900`, `scotus/73500268`, `scotus/73500579`, `scotus/9026000139`, `scotus/9026005216`, `scotus/73280412`, `scotus/73280426`, `scotus/73393227`, `scotus/73500363`, `scotus/9026000048`).
4. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 20`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 20 recent 2020s SCOTUS dockets.
5. `uv run fedcourts query --court scotus --judge Niemeyer --era 2020s --limit 15`
   - `ranged corpus reads: 660 GET(s), 172818432 byte(s)`
   - Returned 0 rows (sparse `--judge` column on live-channel SCOTUS rows).
6. `uv run fedcourts query --court scotus --docket-number 26-516`
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Returned the corpus row for `scotus/9026000516` (`Catherine Elizabeth Chollet, aka Liza Chollet, and Michael Elliot Kohn v. United States`).
7. `uv run fedcourts query --court scotus --party "Simmons" --era 2020s --include-open --limit 10`
   - Rejected by CLI (`No such option: --party`).

## 2. CourtListener MCP Calls
1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Abouammo v. United States", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions", "syllabus"])`
   - Located *Abouammo v. United States*, No. 25-5146 (decided June 11, 2026; `cluster_id: 10862022`, `opinion_id: 11343328`, revised slip opinion `cluster_id: 10875833`, `opinion_id: 11357113`).
2. `mcp_courtlistener_read_document(opinion_id=11343328, chunk_index=0, chunk_size=12000)` and `mcp_courtlistener_read_document(opinion_id=11343328, chunk_index=[1, 2], chunk_size=12000)`
   - Read the full opinion of the Court (per Justice Kagan) in *Abouammo v. United States*, 608 U.S. 597 (2026).
3. `mcp_courtlistener_search(type="o", court="scotus", q=""Abouammo"", fields=["caseName", "dateFiled", "docketNumber", "snippet"])`
   - Returned 2 results (the original and revised slip opinions in *Abouammo v. United States*).
4. `mcp_courtlistener_search(type="o", q=""Abouammo" "7206" OR "Abouammo" "venue"", filed_after="2026-06-11", fields=["caseName", "court", "dateFiled", "docketNumber", "snippet"])`
   - Returned 7 lower-court and SCOTUS decisions citing *Abouammo* on venue (`Abouammo` (2 versions), `United States v. Gessen` (9th Cir.), `United States v. Gonzalez` (1st Cir.), `United States v. Cooper` (1st Cir.), `United States v. Foote O'Donoghue` (D.D.C.), and `United States v. Rodriguez-Arias` (D.P.R.)).
5. `mcp_courtlistener_search(type="o", case_name="Gessen", filed_after="2026-06-11", fields=["caseName", "court", "dateFiled", "docketNumber", "opinions"])`
   - Returned *United States v. Gessen*, No. 24-2979 (9th Cir. Oct. 16, 2026) (`opinion_id: 11436742`).
6. `mcp_courtlistener_search(type="o", case_name="Foote O'Donoghue", filed_after="2026-06-11", fields=["caseName", "court", "dateFiled", "docketNumber", "opinions"])`
   - Returned *United States v. Foote O'Donoghue*, No. 24-cr-0253 (D.D.C. July 22, 2026) (`opinion_id: 11401533`).
7. `mcp_courtlistener_search(type="d", court="scotus", case_name="Whitehead v. United States", fields=["caseName", "dateFiled", "docketNumber", "docket_id"])`
   - Returned 0 results.
8. `mcp_courtlistener_search(type="d", case_name="Chollet", fields=["caseName", "court", "dateFiled", "docketNumber", "docket_id"])`
   - Returned 18 dockets, including Fourth Circuit docket `24-4634` (*United States v. Catherine Chollet*, `docket_id: 69435390`) and WDNC docket `5:22-cr-00060` (`docket_id: 65624112`).
9. `mcp_courtlistener_search_document(opinion_id=[11436742, 11401533], query="Abouammo", snippet_size=500)`
   - Searched *Gessen* and *Foote O'Donoghue* for discussions of *Abouammo*.
10. `mcp_courtlistener_read_document(opinion_id=11401533, chunk_index=[2, 3, 4, 5, 6], chunk_size=8000)` and `mcp_courtlistener_read_document(opinion_id=11401533, chunk_index=[7, 8, 9, 10], chunk_size=8000)`
    - Read D.D.C. analysis of *Abouammo* and venue for false-subscription charges under 26 U.S.C. § 7206(1) and tax evasion under 26 U.S.C. § 7201.
11. `mcp_courtlistener_search(type="o", court="ca1", case_name="Gonzalez", filed_after="2026-06-11", fields=["caseName", "dateFiled", "docketNumber", "opinions"])` and `mcp_courtlistener_search(type="o", court="ca1", case_name="Cooper", filed_after="2026-06-11", fields=["caseName", "dateFiled", "docketNumber", "opinions"])`
    - Located *United States v. Gonzalez*, No. 24-2086 (1st Cir. Aug. 3, 2026) (`opinion_id: 11405068`) and *United States v. Cooper*, No. 24-1769 (1st Cir. Aug. 6, 2026) (`opinion_id: 11409062`).
12. `mcp_courtlistener_search_document(opinion_id=[11405068, 11409062], query="Abouammo", snippet_size=500)`
    - Searched *Gonzalez* and *Cooper* for citations to *Abouammo*.
13. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"id": 69435390, "fields": ["id", "case_name", "docket_number", "date_filed", "date_terminated"]})` and `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69435390, "fields": ["id", "date_filed", "entry_number", "description"]})`
    - Checked Fourth Circuit docket `24-4634` metadata and entry dates.

## 3. Web Searches
- None attempted.
