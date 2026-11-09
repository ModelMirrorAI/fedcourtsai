# Retrieval Log

## 1. Corpus CLI Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "73539054" --event "evt-order-relist-disposition" --role predictor`
   - Resolved paths for `scotus/73539054` (no ranged corpus reads).
2. `uv run fedcourts open-events --case "scotus/73539054"` (failed: `--case` is not a valid option; re-ran with `--court scotus --docket 73539054`).
3. `uv run fedcourts open-events --court scotus --docket 73539054`
   - Returned open events `evt-order-relist-disposition` and `evt-petition-disposition` (no ranged corpus reads line).
4. `uv run fedcourts query --court scotus --docket-number "25-1422"`
   - `ranged corpus reads: 39 GET(s), 9896754 byte(s)`
   - Returned 1 row: `scotus/73539054`, *Sprint Corporation, nka Sprint LLC, et al. v. Federal Communications Commission, et al.* (`distribution_count: 2`, open).
5. `uv run fedcourts query --court scotus --docket-number "25-406"`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 1 row: `scotus/73221533`, *Federal Communications Commission, et al. v. AT&T, Inc.* (granted 2026-01-09, argued 2026-04-21, decided 2026-06-04, reversed and remanded).
6. `uv run fedcourts query --court scotus --docket-number "25-567"`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 1 row: `scotus/73317202`, *Verizon Communications Inc. v. Federal Communications Commission, et al.* (granted 2026-01-09, argued 2026-04-21, decided 2026-06-04, affirmed).
7. `uv run fedcourts query --court scotus --limit 20`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 20 resolved SCOTUS cert petitions from the November 6, 2026 Conference (decided 2026-11-09).
8. `uv run fedcourts query --court scotus --disposition gvr --limit 20`
   - `ranged corpus reads: 38 GET(s), 9895936 byte(s)`
   - Returned 20 recent SCOTUS GVR dispositions across October–November 2026 conferences.
9. `uv run fedcourts query --court scotus --disposition granted --limit 20`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 20 recent SCOTUS granted dispositions.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", citation="608 U.S. 531", fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])`
   - Returned 7 older opinions matching volume/page substrings; did not match *FCC v. AT&T, Inc.* (2026) because Volume 608 page numbers are not yet indexed in the citation array on CourtListener.
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Federal Communications Commission v. AT&T", fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])`
   - Returned the 2010–2011 FOIA case (*FCC v. AT&T Inc.*, 562 U.S. 397 (2011)).
3. `mcp_courtlistener_search(type="o", court="scotus", docket_number="25-406", fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])`
   - Returned 1 result: *FCC v. AT&T*, No. 25-406, `cluster_id: 10870061`, `opinion_id: 11337518`, decided June 4, 2026.
4. `mcp_courtlistener_search(type="o", court="scotus", q="forfeiture Seventh Amendment", filed_after="2026-06-01", filed_before="2026-06-10")`
   - Returned 2 results: *FCC v. AT&T* (`cluster_id: 10870061`, `opinion_id: 11337518`) and *Sripetch v. SEC* (`cluster_id: 10870059`).
5. `mcp_courtlistener_read_document(opinion_id=11337518, chunk_index=[0, 1, 2, 3], chunk_size=8000)`
   - Read chunks 0–3 of the slip opinion in *FCC v. AT&T, Inc.*, No. 25-406 (together with *Verizon Communications, Inc. v. FCC*, No. 25-567), decided June 4, 2026.
6. `mcp_courtlistener_read_document(opinion_id=11337518, chunk_index=[4, 5, 6, 7, 8], chunk_size=8000)`
   - Read chunks 4–8 (the remainder of Chief Justice Roberts's 8–1 majority opinion, including Footnote 5 on p. 14, and Justice Thomas's dissenting opinion in full).
