# Retrieval Log

## 1. Corpus Tooling (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "72406996" --event "evt-brief-response-disposition" --role predictor`
   - Result: resolved `case_id = scotus/72406996`, `corpus = corpus/corpus.db`, `event = data/cases/scotus/72406996/events/evt-brief-response-disposition/event.yaml`.
2. `uv run fedcourts query --help`
   - Result: displayed CLI usage and filter flags.
3. `uv run fedcourts query --court scotus --era 2010s --decided-before 2016 --limit 10`
   - Transfer line: `ranged corpus reads: 917 GET(s), 240123904 byte(s)`
   - Result: returned 10 resolved SCOTUS priors from the 2010s era decided before 2016.
4. `uv run fedcourts query --court scotus --docket-number 16-595 --decided-before 2016-11-03`
   - Transfer line: `ranged corpus reads: 655 GET(s), 171442176 byte(s)`
   - Result: returned 1 row (`scotus/65626698`, `docket_number: "16-595"`, `date_filed: "2016-11-03"`, `originating_court: "ala"`, all decision fields masked under `--decided-before 2016-11-03`).
5. `uv run fedcourts query --court scotus --docket-number 16A451 --decided-before 2016-11-03`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: `note: docket-number lookup: no row for 16A451 (scotus) — the corpus holds no such number in scope, the other filters screened it, or the replay clock does not admit it`.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Arthur v. Dunn", filed_before="2016-11-03")`
   - Result: 2 opinions returned (District Court M.D. Ala. opinions in *Arthur v. Dunn*, 2016 WL 1551475 (`opinion_id: 7239047`, filed 2016-04-15) and 480 F. Supp. 2d 1277 (`opinion_id: 237187`, filed 2007-03-28)).
2. `mcp_courtlistener_search(type="o", case_name="Arthur v. State", q=""Thomas Douglas Arthur" "1951985"", filed_before="2016-11-03")`
   - Result: 1 opinion returned (*Arthur v. State*, Ala. Crim. App. No. CR-15-1452, 236 So. 3d 155, filed 2016-10-19, `opinion_id: 4867831` / `cluster_id: 5053254`, summary affirmance; citation metadata contained Westlaw subsequent history string).
3. `mcp_courtlistener_search(type="o", court="ala", q=""Thomas Douglas Arthur" OR "1951985"", filed_after="2016-01-01", filed_before="2016-11-03")`
   - Result: 0 results.
4. `mcp_courtlistener_search(type="o", court="ca11", q=""Thomas D. Arthur" OR "Thomas Douglas Arthur"", filed_after="2016-01-01", filed_before="2016-11-03")`
   - Result: 1 cluster returned (*Arthur v. Commissioner, Alabama Department of Corrections*, 840 F.3d 1268, 11th Cir. No. 16-15549, filed 2016-11-02, `opinion_id: 9837745` majority, `opinion_id: 9837746` dissent by Judge Wilson).
5. `mcp_courtlistener_read_document(opinion_id=7239047, chunk_index=0)`
   - Result: read chunk 0 of M.D. Ala. April 15, 2016 opinion in *Arthur v. Dunn*.
6. `mcp_courtlistener_read_document(opinion_id=9837745, chunk_index=[0, 1])`
   - Result: read chunks 0 and 1 of 11th Cir. Nov. 2, 2016 majority opinion in *Arthur v. Commissioner, Alabama Department of Corrections*, 840 F.3d 1268.
7. `mcp_courtlistener_read_document(opinion_id=9837746, chunk_index=0)`
   - Result: read chunk 0 of Judge Wilson's dissent in *Arthur v. Commissioner, Alabama Department of Corrections*, 840 F.3d 1268.
8. `mcp_courtlistener_read_document(opinion_id=9837745, chunk_index=[2, 3])`
   - Result: read chunks 2 and 3 of 11th Cir. majority opinion in *Arthur v. Commissioner, Alabama Department of Corrections*.
9. `mcp_courtlistener_search(type="o", court="ala", q=""Thomas Douglas Arthur"", filed_before="2016-11-03")`
   - Result: 5 results returned (prior Alabama Supreme Court decisions in *Ex parte Arthur*, Docket No. `1951985`, from 1985, 1991, 1997, 2007, and 2008).
10. `mcp_courtlistener_search_document(opinion_id=9837745, query="Hurst")`
    - Result: 0 matches.
11. `mcp_courtlistener_search_document(opinion_id=9837745, query="1951985")`
    - Result: 0 matches.
12. `mcp_courtlistener_search_document(opinion_id=9837745, query="Rule 32")`
    - Result: 0 matches.
13. `mcp_courtlistener_search(type="o", court="alacrimapp", q=""Arthur"", filed_after="2015-01-01", filed_before="2016-11-03")`
    - Result: 35 results returned (unrelated Alabama Court of Criminal Appeals table dispositions).
14. `mcp_courtlistener_search(type="o", q=""Hurst v. Florida" "Alabama" "override" OR "1951985"", filed_after="2016-01-01", filed_before="2016-11-03")`
    - Result: 19 results returned, including SCOTUS *Hurst* GVRs in Alabama direct appeals (*Kirksey v. Alabama*, *Russell v. Alabama*, *Johnson v. Alabama*, *Wimbley v. Alabama*) and the Alabama Supreme Court's decision in *Ex parte Bohannon*, 222 So. 3d 525 (Ala. Sept. 30, 2016, `opinion_id: 4842426`).
15. `mcp_courtlistener_search(type="o", court="scotus", q=""Alabama" "Hurst" OR "Arthur"", filed_after="2016-01-01", filed_before="2016-11-03")`
    - Result: 90 results returned, including November 3, 2016 SCOTUS orders in companion application `16A451` / `16-602` (*Arthur v. Dunn*, 137 S. Ct. 14 and 137 S. Ct. 15) and Alabama *Hurst* / *Montgomery* orders.
16. `mcp_courtlistener_read_document(opinion_id=4842426, chunk_index=0)`
    - Result: read chunk 0 of the Alabama Supreme Court's opinion in *Ex parte Bohannon*, 222 So. 3d 525 (Ala. Sept. 30, 2016).
