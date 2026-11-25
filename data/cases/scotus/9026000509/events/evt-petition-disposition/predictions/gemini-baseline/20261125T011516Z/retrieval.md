# Retrieval Log

## 1. Corpus CLI (`fedcourts`) Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000509" --event "evt-petition-disposition" --role predictor && uv run fedcourts query --help`
   - Result: Resolved cell paths (`case_id: scotus/9026000509`, `event: data/cases/scotus/9026000509/events/evt-petition-disposition/event.yaml`) and printed `fedcourts query` CLI usage options. No ranged corpus reads.
2. `uv run fedcourts query --court scotus --era modern --stage cert --search "Title VII retaliation reasonable belief opposition clause summary judgment" --limit 15`
   - Result: CLI usage error (`No such option: --stage`, displaying structured filter flags). No ranged corpus reads.
3. `uv run fedcourts query --court scotus --era modern --stage cert --search "1981 statute of limitations 1658 Jones Donnelley retaliation" --limit 15`
   - Result: CLI usage error (`No such option: --stage`, displaying structured filter flags). No ranged corpus reads.
4. `uv run fedcourts query --court scotus --era 2020s --limit 10 && uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 10`
   - Result: Returned 10 recent 2020s SCOTUS corpus rows (and queried `summary-reversal` rows in the 2020s slice).
   - Stderr stats line: `ranged corpus reads: 7 GET(s), 1769472 byte(s)` (on first command).
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8 && uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - Result: Returned 8 recent 2020s SCOTUS granted petitions and 5 recent 2020s SCOTUS GVR petitions for comparison of relist/CVSG/amicus profiles.
   - Stderr stats line: `ranged corpus reads: 3 GET(s), 786432 byte(s)` (on first command).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="ca5", docket_number="25-11255", fields=["caseName", "court_id", "dateFiled", "docketNumber", "cluster_id", "opinions", "snippet"])`
   - Result: `count: 0` (`query_id: 819b8f30`), confirming no published or unpublished opinion text was issued by the Fifth Circuit in No. 25-11255 (summary affirmance without opinion under 5th Cir. R. 47.6, matching Appendix B).
2. `mcp_courtlistener_search(type="o", court="ca5", case_name="Areizaga", fields=["caseName", "court_id", "dateFiled", "docketNumber", "cluster_id", "opinions", "snippet"])`
   - Result: `count: 0` (`query_id: 9c67ffa3`).
3. `mcp_courtlistener_search(type="o", court="scotus", q='"2000e-3(a)" "reasonable belief" OR "opposition clause"', fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "snippet"])`
   - Result: `count: 26` (`query_id: 9cda6669`), returning governing Supreme Court Title VII retaliation precedents including *Crawford v. Metropolitan Government of Nashville & Davidson County*, 555 U.S. 271 (2009), *University of Texas Southwestern Medical Center v. Nassar*, 570 U.S. 338 (2013), *Thompson v. North American Stainless, LP*, 562 U.S. 170 (2011), and *Clark County School District v. Breeden*, 532 U.S. 268 (2001).
4. `mcp_courtlistener_search(type="o", court="ca5", q='"1658" "1981" retaliation "four-year" OR "two-year"', fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "snippet"])`
   - Result: `count: 6` (`query_id: 3ff421aa`), including *Stelly v. Department of Public Safety*, No. 24-30550 (5th Cir. Aug. 15, 2025), and *Taylor v. United Parcel Service, Inc.*, 554 F.3d 510 (5th Cir. 2008).
5. `mcp_courtlistener_search(type="r", court="ntxd", docket_number="4:22-cv-00703", fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
   - Result: Validation error (`Invalid value 'ntxd' for court`; N.D. Tex. code is `txnd`).
6. `mcp_courtlistener_search(type="d", court="ca5", docket_number="25-11255", fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
   - Result: `count: 0` (`query_id: 65fac7c4`).
7. `mcp_courtlistener_read_document(opinion_id=11121461, chunk_index=0)`
   - Result: Read chunk 0 of *Stelly v. Department of Public Safety*, No. 24-30550 (5th Cir. Aug. 15, 2025) (`total_chars: 43601`, `total_chunks: 6`).
8. `mcp_courtlistener_search(type="r", court="txnd", docket_number="4:22-cv-00703", fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
   - Result: `count: 1` (`query_id: 977c26ef`, *Areizaga v. TForce Freight Inc.*, N.D. Tex. No. 4:22-cv-00703, `dateFiled: 2022-08-15`, `docket_id: 64893531`).
9. `mcp_courtlistener_read_document(opinion_id=11121461, chunk_index=[3, 4, 5])`
   - Result: Read chunks 3–5 of *Stelly v. Department of Public Safety*, No. 24-30550 (5th Cir. Aug. 15, 2025), reviewing current Fifth Circuit summary-judgment and § 1981 / Title VII treatment.

## 3. Web Searches

None attempted.
