# Retrieval Log

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000420" --event "evt-petition-disposition" --role predictor`
   - Resolved case (`scotus/9026000420`), corpus (`corpus/corpus.db`), and event path (`data/cases/scotus/9026000420/events/evt-petition-disposition/event.yaml`).
2. `uv run fedcourts query --help`
   - Inspected structured filter flags for `fedcourts query`.
3. `uv run fedcourts query --court scotus --docket-number 26-1`
   - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned `scotus/9026000001` (*Sunoco, Inc. (R&M), et al. v. Perry Cline*, No. 26-1), showing `disposition: "denied"`, `date_cert_denied: "2026-10-05"`.
4. `uv run fedcourts query --court scotus --docket-number 25-677`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/73279523` (*City of Cleveland, Ohio v. Albert Pickett, Jr.*, No. 25-677), showing `disposition: null`, `distribution_count: 4`, `last_live_polled: "2026-10-26"`.
5. `uv run fedcourts query --court scotus --docket-number 25-625`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/73279069` (*Takeda Pharmaceutical Company Limited v. Painters and Allied Trades District Council 82 Health Care Fund*, No. 25-625), showing `disposition: "denied"`, `date_cert_denied: "2026-03-23"`.
6. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Returned 10 recent OT2026 granted petitions and applications for comparative context.
7. `uv run fedcourts query --court scotus --docket-number 24-304`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/69981163` (*Laboratory Corporation of America Holdings, dba Labcorp v. Luke Davis*, No. 24-304), showing `disposition: "granted"`, `merits_judgment: "dismissed-as-improvidently-granted"`, `merits_decided: "2025-06-05"`.
8. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 5 recent 2020s denied SCOTUS matters.
9. `uv run fedcourts query --court scotus --judge "Dennis Jacobs" --judge "Pierre N. Leval" --judge "Michael H. Park" --limit 10`
   - `ranged corpus reads: 656 GET(s), 171900928 byte(s)`
   - Returned 0 matching SCOTUS rows (expected since `--judge` matches SCOTUS authoring justices on historical rows rather than lower-court panel judges).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="ca2", case_name="Old Jericho Enterprise", fields=["caseName", "docketNumber", "dateFiled", "citation", "cluster_id"])`
   - Returned `count: 0` (the July 8, 2026 Second Circuit opinion in *Old Jericho Enterprise, Inc. v. Visa Inc.* is already reproduced in full in `record/documents/petition.txt` Appendix B).
2. `mcp_courtlistener_search(type="d", case_name="Jack Rabbit", fields=["caseName", "docketNumber", "dateFiled", "court_id"])`
   - Returned 18 unrelated district/bankruptcy court dockets involving "Jack Rabbit" entities.
3. `mcp_courtlistener_search(type="o", citation="62 F.4th 704", fields=["caseName", "docketNumber", "dateFiled", "citation", "cluster_id", "opinions"])`
   - Returned `count: 0`.
4. `mcp_courtlistener_search(type="o", court="scotus", q=""Jack Rabbit" OR "Fikes Wholesale" OR "Old Jericho"", fields=["caseName", "docketNumber", "dateFiled", "citation"])`
   - Returned `count: 0`.

## 3. Web Searches

None attempted.
