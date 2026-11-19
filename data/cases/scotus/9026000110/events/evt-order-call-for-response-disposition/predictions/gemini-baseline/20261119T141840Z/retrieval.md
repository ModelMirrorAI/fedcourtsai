# Retrieval Log

All lookups consulted beyond the provisioned case inputs (`data/cases/scotus/9026000110/record/` and `event.yaml`) and committed `metrics/statpack.md`:

## 1. Local CLI Inspection (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000110" --event "evt-order-call-for-response-disposition" --role predictor` and `uv run fedcourts query --help`
   - Confirmed cell paths and CLI query flags (no corpus reads).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
   - Returned 10 recent 2020s SCOTUS granted dockets (`25-944`, `26-239`, `26A560`, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`) for schema and distribution-count context.

3. `uv run fedcourts query --court scotus --citation "594 U.S. 474" --citation "144 S. Ct. 264" --citation "598 U.S. 631"`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows (note on sparse `citations` column in `scotus` scope).

4. `uv run fedcourts query --court scotus --docket-number 22-1130`
   - Stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned 1 row: *74 Pinehurst LLC, et al. v. New York, et al.* (`scotus/68263638`), `disposition: "denied"` on `2024-02-20`, `distribution_count: 13`.

5. `uv run fedcourts query --court scotus --docket-number 22-1095`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: *Community Housing Improvement Program, et al. v. City of New York, New York, et al.* (`scotus/72475274`), `disposition: "denied"` on `2023-10-02`, `distribution_count: 1`.

6. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - Stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Returned 5 recent 2020s SCOTUS GVR priors (`25-1421`, `26-5528`, `25-442`, `25-1348`, `26-5123`).

7. `uv run fedcourts query --court scotus --docket-number 22-1170`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: *335-7 LLC, et al. v. City of New York, New York, et al.* (`scotus/72475355`), `disposition: "denied"` on `2024-02-20`, `distribution_count: 13`.

8. `uv run fedcourts query --court scotus --docket-number 24-781`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: *First Choice Women's Resource Centers, Inc. v. Jennifer Davenport, Attorney General of New Jersey* (`scotus/71983743`), `disposition: "granted"` (`2025-06-16`), `merits_decided: "2026-04-29"`, `merits_judgment: "reversed"`.

9. `uv run fedcourts query --court scotus --docket-number 24-435`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: *GHP Management Corporation, et al. v. City of Los Angeles, California, et al.* (`scotus/70670982`), `disposition: "denied"` on `2025-06-30`, `distribution_count: 14`.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca4", case_name="Walls v. Prince George's County", fields=[...])`
   - Returned 0 results (default status filter excluded unpublished opinions).

2. `mcp_courtlistener_search(type="o", case_name="74 Pinehurst", fields=[...])`
   - Returned 1 result: *74 Pinehurst LLC v. State of New York*, 59 F.4th 557 (2d Cir. 2023) (`cluster_id: 9373171`).

3. `mcp_courtlistener_search(type="o", court="ca4", docket_number="25-1121", fields=[...])`
   - Returned 0 results (default status filter excluded unpublished opinions).

4. `mcp_courtlistener_search(type="o", court="scotus", q=""74 Pinehurst"")`
   - Returned 0 results (default status filter excluded `Relating-to` order-list statements).

5. `mcp_courtlistener_search(type="o", court="ca4", docket_number="25-1121", stat_Published=true, stat_Unpublished=true, fields=[...])`
   - Returned 1 result: *Garnell Walls v. Prince George's County*, No. 25-1121 (4th Cir. Feb. 23, 2026) (`cluster_id: 10799867`, `opinion_id: 11266543`, unpublished).

6. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2024-02-19", filed_before="2024-02-22", stat_Published=true, stat_Relating-to=true, stat_Separate=true, stat_Unpublished=true, fields=[...])`
   - Returned 9 results, including Statement of Thomas, J., respecting denial of certiorari in *74 Pinehurst LLC v. New York* & *335-7 LLC v. City of New York*, Nos. 22-1130 & 22-1170 (`cluster_id: 9476534`, `opinion_id: 9942065`).

7. `mcp_courtlistener_search(type="o", q=""Garnell Walls"", stat_Published=true, stat_Unpublished=true, fields=[...])`
   - Returned 2 results (*Garnell Walls v. Prince George's County*, CA4 2026-02-23, and an unrelated 2000 CA4 opinion).

8. `mcp_courtlistener_search(type="o", court="scotus", q=""rent stabilization" OR "74 Pinehurst" OR "Pakdel"", stat_Published=true, stat_Relating-to=true, stat_Separate=true, fields=[...])`
   - Returned 11 results, including *74 Pinehurst* (`opinion_id: 9942065`), *First Choice Women's Resource Centers, Inc. v. Davenport* (`opinion_id: 11317513`, decided 2026-04-29), and *Pakdel v. City and County of San Francisco*, 594 U.S. 474 (2021) (`opinion_id: 4699044`).

9. `mcp_courtlistener_read_document(opinion_id=11266543)`
   - Read full text (24,435 chars) of *Garnell Walls v. Prince George's County*, No. 25-1121 (4th Cir. Feb. 23, 2026), the decision below in vided-amicus companion No. 26-107.

10. `mcp_courtlistener_read_document(opinion_id=9942065)`
    - Read full text (2,956 chars) of Statement of Thomas, J., respecting denial of certiorari in *74 Pinehurst LLC v. New York*, Nos. 22-1130 & 22-1170 (Feb. 20, 2024).

11. `mcp_courtlistener_read_document(opinion_id=4699044)`
    - Read full text (19,276 chars) of *Pakdel v. City and County of San Francisco*, 594 U.S. 474 (2021) (per curiam).

12. `mcp_courtlistener_search_document(opinion_id=11317513, query="ripeness", snippet_size=500)`
    - Returned 0 matches in *First Choice Women's Resource Centers, Inc. v. Davenport* (No. 24-781, Apr. 29, 2026).

13. `mcp_courtlistener_search_document(opinion_id=11317513, query="Pakdel", snippet_size=500)`
    - Returned 5 matches in *First Choice Women's Resource Centers, Inc. v. Davenport*.

14. `mcp_courtlistener_search_document(opinion_id=11317513, query="ripe", snippet_size=500)`
    - Returned 1 match in *First Choice Women's Resource Centers, Inc. v. Davenport*.

15. `mcp_courtlistener_search(type="o", q=""Building and Realty Institute of Westchester" OR "GHP Management"", stat_Published=true, stat_Relating-to=true, stat_Unpublished=true, fields=[...])`
    - Returned 10 results, including *GHP Management Corp. v. City of Los Angeles*, SCOTUS No. 24-435 (`2025-06-30`), and *Building and Realty Institute v. State of New York*, CA2 (`2024-03-12`).

16. `mcp_courtlistener_search(type="o", court="scotus", docket_number="24-435", stat_Published=true, stat_Relating-to=true, stat_Separate=true, fields=[...])`
    - Returned 1 result: *GHP Management Corp. v. City of Los Angeles*, No. 24-435 (`cluster_id: 10619930`, `opinion_id: 11086518`).

17. `mcp_courtlistener_read_document(opinion_id=11086518)`
    - Read full text (8,860 chars) of Dissent of Thomas, J. (joined by Gorsuch, J.) from denial of certiorari in *GHP Management Corp. v. City of Los Angeles*, No. 24-435 (June 30, 2025).

18. `mcp_courtlistener_read_document(opinion_id=11317513, chunk_index=[4, 5, 6])`
    - Read chunks 4–6 of *First Choice Women's Resource Centers, Inc. v. Davenport*, No. 24-781 (Apr. 29, 2026), discussing § 1983, *Knick*, and *Pakdel*.

19. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2024-03-01", q=""Pakdel" OR "Williamson County" OR "Rent Stabilization"", stat_Published=true, stat_Relating-to=true, stat_Separate=true, fields=[...])`
    - Returned 1 result (*First Choice Women's Resource Centers, Inc. v. Davenport*).

20. `mcp_courtlistener_search(type="d", court="scotus", case_name="Building and Realty Institute")`
    - Returned 0 results.

21. `mcp_courtlistener_search(type="d", court="scotus", case_name="G-Max Management")`
    - Returned 0 results.

22. `mcp_courtlistener_search(type="o", court="scotus", q=""G-Max" OR "Building and Realty"", stat_Published=true, stat_Relating-to=true, stat_Unpublished=true)`
    - Returned 1 unrelated result (*Omni Capital International, Ltd. v. Rudolf Wolff & Co.*, 484 U.S. 97).

23. `mcp_courtlistener_search(type="o", case_name="Tedford's Tenancy", stat_Published=true, stat_Unpublished=true)`
    - Returned 1 result: *Tedford's Tenancy, LLC v. City of New York*, 2025 NY Slip Op 03152 (N.Y. App. Div. May 22, 2025) (`opinion_id: 11056577`, matching `record/documents/appendix.txt` App. 1a–4a).

24. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=9373171, fields=["id", "case_name", "sub_opinions"])`
    - Retrieved `opinion_id: 9368647` for *74 Pinehurst LLC v. State of New York*, 59 F.4th 557 (2d Cir. 2023).

25. `mcp_courtlistener_search_document(opinion_id=9368647, query="hardship", snippet_size=500)`
    - Returned 6 matches in *74 Pinehurst* (2d Cir. 2023) on RSL hardship exemptions and *Pakdel* ripeness.

26. `mcp_courtlistener_search_document(opinion_id=9368647, query="ripe", snippet_size=500)`
    - Returned 5 matches in *74 Pinehurst* (2d Cir. 2023).

## 3. Web Searches

None attempted.
