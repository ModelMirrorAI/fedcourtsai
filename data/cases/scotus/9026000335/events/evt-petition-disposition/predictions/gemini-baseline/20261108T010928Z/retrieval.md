# Retrieval Log

## 1. `fedcourts query` Calls

1. `uv run fedcourts query --court scotus --docket-number 26-199`
   - Stderr: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Returned: `scotus/9026000199` (*Horseracing Integrity and Safety Authority, Incorporated, et al. v. National Horsemen's Benevolent and Protective Association, et al.*, No. 26-199).
2. `uv run fedcourts query --court scotus --docket-number 26-201`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/9026000201` (*Federal Trade Commission, et al. v. National Horsemen's Benevolent and Protective Association, et al.*, No. 26-201).
3. `uv run fedcourts query --court scotus --docket-number 26-430`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: `scotus/9026000430` (*National Horsemen's Benevolent and Protective Association, et al. v. Horseracing Integrity and Safety Authority, Incorporated, et al.*, No. 26-430).
4. `uv run fedcourts query --court scotus --docket-number 25-1325`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: `scotus/73500226` (*Oklahoma v. United States*, No. 25-1325).
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
   - Returned: 10 recent OT2026 granted petitions/applications (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`).
6. `uv run fedcourts query --court scotus --docket-number 24-465`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: `scotus/72484176` (*Texas, et al. v. Jerry Black, et al.*, No. 24-465, GVR'd 2025-06-30).
7. `uv run fedcourts query --court scotus --docket-number 24-429`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/72484140` (*Federal Trade Commission, et al. v. National Horsemen's Benevolent and Protective Association, et al.*, No. 24-429, GVR'd 2025-06-30).
8. `uv run fedcourts query --court scotus --docket-number 24-433`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/72484144` (*Horseracing Integrity and Safety Authority, Incorporated, et al. v. National Horsemen's Benevolent and Protective Association, et al.*, No. 24-433, GVR'd 2025-06-30).
9. `uv run fedcourts query --court scotus --judge "Duncan" --limit 20`
   - Stderr: `ranged corpus reads: 699 GET(s), 183107584 byte(s)`
   - Returned: 1 historical case (`scotus/120`, 01-8721).
10. `uv run fedcourts query --court scotus --citation "606 U.S. 656" --limit 10`
    - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
    - Returned: 0 rows (note on parallel cites filter).
11. `uv run fedcourts query --court scotus --docket-number 24-472`
    - Stderr: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
    - Returned: `scotus/72484185` (*National Horsemen's Benevolent and Protective Association, et al. v. Horseracing Integrity and Safety Authority, Inc., et al.*, No. 24-472, GVR'd 2025-06-30).
12. `uv run fedcourts query --court scotus --docket-number 24-489`
    - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: `scotus/72484202` (*Gulf Coast Racing, L.L.C., et al. v. Horseracing Integrity and Safety Authority, Inc., et al.*, No. 24-489, GVR'd 2025-06-30).
13. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
    - Stderr: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
    - Returned: 10 recent OT2026 denied applications.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="ca5", case_name="National Horsemen's Benevolent")`
   - Returned: 1 result (*National Horsemen's Benevolent v. Black*, 53 F.4th 869, No. 22-10387, cluster 8515308).
2. `mcp_courtlistener_search(type="o", court="ca6", case_name="Oklahoma v. United States")`
   - Returned: 1 result (*State of Oklahoma v. United States*, No. 22-5487, filed 2025-12-17, cluster 10760271).
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Consumers' Research")`
   - Returned: 2 results (*FCC v. Consumers' Research*, 606 U.S. 656, No. 24-354, filed 2025-06-27, clusters 10776820 and 10618553).
4. `mcp_courtlistener_search(type="o", court="ca8", case_name="Walmsley v. Federal Trade Commission")`
   - Returned: 0 results.
5. `mcp_courtlistener_search(type="o", docket_number="23-10520")`
   - Returned: 2 results (*Natl Horsemen's Benevolent v. Black*, 107 F.4th 415, filed 2024-07-05, cluster 9997933; and *Natl Horsemen's Benevolent v. Black*, filed 2026-06-11, cluster 10873790).
6. `mcp_courtlistener_read_document(opinion_id=10873790, chunk_index=[4, 5, 6], chunk_size=8000)`
   - Returned: HTTP 404 (10873790 is a cluster ID, not an opinion ID).
7. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10873790, fields=["id", "sub_opinions"])`
   - Returned: `sub_opinions: ["https://www.courtlistener.com/api/rest/v4/opinions/11341261/"]`.
8. `mcp_courtlistener_read_document(opinion_id=11341261, chunk_index=[4, 5, 6, 7], chunk_size=8000)`
   - Returned: `{"doc_type": "opinion", "doc_id": 11341261, "error": "No text is available for this document."}`.

## 3. Web Searches

None.
