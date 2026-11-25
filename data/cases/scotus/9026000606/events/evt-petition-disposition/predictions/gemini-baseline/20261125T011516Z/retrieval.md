# Retrieval Log

## 1. Local CLI Inspection and Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000606" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Local path verification and CLI flag check (no corpus transfer).
2. `uv run fedcourts query --court scotus --citation "513 U.S. 64" --limit 5`
   - Transfer stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (CLI noted that only 195 `scotus` rows populate own parallel citations in `citations`).
3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer stderr: `ranged corpus reads: 7 GET(s), 1769472 byte(s)`
   - Result: Returned 10 recent 2020s resolved SCOTUS rows for baseline context.
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
   - Result: Returned 10 recent granted 2020s SCOTUS cert petitions (confirming typical multi-distribution / amicus / repeat-counsel profiles and checking that none involve 18 U.S.C. § 2251(a) or First Amendment mistake-of-age).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", q='"Wilson" OR "Malloy" OR "Thurber" OR "Pliego" OR "Encarnacion-Ruiz" OR "Deuman" OR "Fletcher"', num_results=20, fields=["caseName", "citation", "dateFiled", "docketNumber", "snippet"])`
   - Result (`query_id: b4c87809`): 7,758 broad name matches across SCOTUS cert orders; refined in query #13 below with `"United States"` and circuit/docket constraints.
2. `mcp_courtlistener_search(type="r", court="sdd", docket_number="3:23-cr-30083", num_results=10, fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
   - Result (`query_id: 1de126f7`): Returned 3 RECAP docket records for *United States v. Kucera* (`docket_id`: `69885943`, `68927035`, `67661923`, filed `2023-08-01`).
3. `mcp_courtlistener_search(type="rd", court="sdd", docket_number="3:23-cr-30083", entry_date_filed_after="2025-10-01", entry_date_filed_before="2025-11-15", num_results=20, fields=["caseName", "docket_entry_id", "document_number", "description", "entry_date_filed", "is_available", "id"])`
   - Result (`query_id: ed59f06d`): Returned 22 sentencing/judgment-era RECAP document entries (entries 202–212), all with `is_available: false` and empty descriptions.
4. `mcp_courtlistener_search(type="d", court="ca8", docket_number="25-3180", num_results=10, fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
   - Result (`query_id: 2c8c6bd1`): 0 RECAP docket results for Eighth Circuit No. 25-3180.
5. `mcp_courtlistener_search(type="o", q='"858 F.2d 534" "2251"', order_by="dateFiled desc", num_results=20, fields=["caseName", "citation", "court_id", "dateFiled", "docketNumber"])`
   - Result (`query_id: 3b8edc15`): Returned 46 appellate opinions citing *Kantor* (`858 F.2d 534`) and `2251`, including *United States v. Kucera* (8th Cir. Aug. 13, 2026), *United States v. Deschambault* (1st Cir. May 18, 2026), *United States v. Thurber*, 106 F.4th 814 (8th Cir. 2024), *United States v. Tyson*, 947 F.3d 139 (3d Cir. 2020), *United States v. Jayavarman*, 871 F.3d 1050 (9th Cir. 2017), *United States v. Henry*, 827 F.3d 16 (1st Cir. 2016), *United States v. Ruggiero*, 791 F.3d 1281 (11th Cir. 2015), and *United States v. Encarnacion-Ruiz*, 787 F.3d 581 (1st Cir. 2015).
6. `mcp_courtlistener_search(type="o", court="scotus", case_name="Thurber v. United States", num_results=10, fields=["caseName", "citation", "dateFiled", "docketNumber"])`
   - Result (`query_id: da3b7ab5`): 0 results.
7. `mcp_courtlistener_get_endpoint_item(endpoint_id="docket-entries", item_id=441738892, fields=["id", "entry_number", "date_filed", "description"])`
   - Result: Confirmed entry 206 (`2025-10-22`, judgment date) in `3:23-cr-30083` carried an empty description in RECAP.
8. `mcp_courtlistener_search(type="o", court="ca1", case_name="United States v. Deschambault", num_results=5, fields=["caseName", "citation", "cluster_id", "dateFiled", "docketNumber", "opinions"])`
   - Result (`query_id: 433339e0`): Returned *United States v. Deschambault*, No. 24-1275 (`cluster_id: 10860829`, `opinion_id: 11328241`, filed `2026-05-18`).
9. `mcp_courtlistener_search(type="d", court="scotus", party_name="Deschambault", num_results=10, fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
   - Result (`query_id: 88e27c06`): 0 SCOTUS docket results.
10. `mcp_courtlistener_search(type="d", court="scotus", party_name="Thurber", num_results=10, fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
    - Result (`query_id: 8df1e4b0`): 0 SCOTUS docket results.
11. `mcp_courtlistener_search_document(opinion_id=11328241, query="mistake", snippet_size=400)`
    - Result: 8 matches in *United States v. Deschambault* (1st Cir. May 18, 2026), confirming the First Circuit's recent reaffirmation that mistake of age is not a permissible defense under 18 U.S.C. § 2251(a) and noting that *Kantor* (9th Cir. 1988) predated *X-Citement Video* and has found no acceptance in any other circuit.
12. `mcp_courtlistener_search(type="rd", court="sdd", docket_number="3:23-cr-30083", available_only=true, order_by="entry_date_filed desc", num_results=20, fields=["docket_entry_id", "document_number", "description", "short_description", "entry_date_filed", "id"])`
    - Result (`query_id: bf70bf9e`): Returned 2 available pretrial suppression orders from February and July 2024 (entries 67 and 80); sentencing judgment was not available in RECAP.
13. `mcp_courtlistener_search(type="o", court="scotus", q='("Malloy v. United States" AND ("568 F.3d" OR "09-")) OR ("Wilson v. United States" AND "09-") OR ("Fletcher v. United States" AND "11-") OR ("Humphrey v. United States" AND "10-") OR ("Ruggiero v. United States" AND "15-") OR ("Tyson v. United States" AND "20-") OR ("Deschambault v. United States")', order_by="dateFiled desc", num_results=25, fields=["caseName", "citation", "dateFiled", "docketNumber"])`
    - Result (`query_id: ec30aede`): Confirmed prior Supreme Court certiorari denials on the 18 U.S.C. § 2251(a) mistake-of-age split, including *Ruggiero v. United States*, 136 S. Ct. 429 (2015) (No. 15-401), *Fletcher v. United States*, 565 U.S. 980 (2011) (No. 11-5253), and *Malloy v. United States*, 559 U.S. 991 (2010) (No. 09-523).

## 3. Web Searches

None attempted.
