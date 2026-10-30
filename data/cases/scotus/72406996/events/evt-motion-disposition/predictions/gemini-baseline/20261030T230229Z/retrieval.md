# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 16-595 --decided-before 2016-11-04`
   - Transfer: `ranged corpus reads: 663 GET(s), 173539328 byte(s)`
   - Returned: `scotus/65626698` (linked cert petition No. 16-595 from `ala`, filed `2016-11-03`, disposition masked under cutoff).
2. `uv run fedcourts query --court scotus --era 2010s --decided-before 2016-11-04 --limit 10`
   - Transfer: `ranged corpus reads: 227 GET(s), 59506688 byte(s)`
   - Returned: 10 resolved SCOTUS priors decided on or before `2016-11-03`, including companion application `scotus/65622632` (`16A451`, *Thomas D. Arthur v. Jefferson S. Dunn, Commissioner, Alabama Department of Corrections, et al.*, originating court `ca11` `16-15549`, decided `2016-11-03`, `referred_to_court: true`, `disposition: granted`) and contemporaneous applications `16A431`, `16A432`, `16A442`, `16A436`, `16A441`, `16A405`, `16A390`, `16A244`, `16A344`.
3. `uv run fedcourts query --court scotus --docket-number 16-602 --decided-before 2016-11-04`
   - Transfer: `ranged corpus reads: 655 GET(s), 171442176 byte(s)`
   - Returned: `scotus/4616502` (companion cert petition No. 16-602 from `ca11`, filed `2016-11-03`, disposition masked under cutoff).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="Arthur v. Dunn", filed_before="2016-11-04")`
   - Returned: 20 opinions, including *Arthur v. Dunn*, 137 S. Ct. 14 (Nov. 3, 2016) (No. 16-602 / 16A451) and *Arthur v. Dunn*, 137 S. Ct. 15 (Nov. 3, 2016) (16A451).
2. `mcp_courtlistener_search(type="o", case_name="Arthur v. Alabama", filed_before="2016-11-04")`
   - Returned: 20 opinions, including *Arthur v. Commissioner, Alabama Department of Corrections*, 840 F.3d 1268 (11th Cir. Nov. 2, 2016) (`opinion_id: 9837745` / `cluster_id: 4317887`).
3. `mcp_courtlistener_search(type="o", docket_number="1951985", filed_before="2016-11-04")`
   - Returned: 3 opinions in Alabama Supreme Court docket `1951985` (*Ex parte Arthur*, 711 So. 2d 1097 (Ala. 1997)).
4. `mcp_courtlistener_read_document(opinion_id=9837745, chunk_index=0, chunk_size=8000)`
   - Read opening chunk of *Arthur v. Commissioner, ADOC*, 840 F.3d 1268 (11th Cir. Nov. 2, 2016).
5. `mcp_courtlistener_search_document(opinion_id=9837745, query="Hurst")`
   - 0 matches.
6. `mcp_courtlistener_search_document(opinion_id=9837745, query="Supreme Court of Alabama")`
   - 0 matches.
7. `mcp_courtlistener_search_document(opinion_id=9837745, query="execution date")`
   - 6 matches detailing the Alabama Supreme Court's order setting Arthur's execution date for November 3, 2016.
8. `mcp_courtlistener_search_document(opinion_id=9837745, query="November 3")`
   - 6 matches detailing the November 3, 2016 execution schedule and procedural history.
9. `mcp_courtlistener_read_document(opinion_id=8396661)`
   - Read full text of *Arthur v. Dunn*, 137 S. Ct. 14 (Nov. 3, 2016) (No. 16-602 / 16A451).
10. `mcp_courtlistener_read_document(opinion_id=8396664)`
    - Read full text of *Arthur v. Dunn*, 137 S. Ct. 15 (Nov. 3, 2016) (No. 16A451).
11. `mcp_courtlistener_search(type="o", case_name="Ex parte Arthur", filed_after="2015-01-01", filed_before="2016-11-04")`
    - Returned 1 unrelated opinion (*Ex parte Douglas Arthur McCormick*).
12. `mcp_courtlistener_search(type="o", case_name="Arthur v. State", filed_after="2015-01-01", filed_before="2016-11-04")`
    - Returned 20 opinions.
13. `mcp_courtlistener_search(type="o", court="ala", q="Arthur", filed_after="2016-01-01", filed_before="2016-11-04")`
    - Returned 7 opinions.
14. `mcp_courtlistener_search(type="o", court="alacrimapp", q="Arthur", filed_after="2015-01-01", filed_before="2016-11-04")`
    - Returned 35 opinions.
15. `mcp_courtlistener_search(type="o", court="scotus", q="Arthur", filed_after="2016-11-01", filed_before="2016-11-04")`
    - Returned 2 opinions (`137 S. Ct. 14` and `137 S. Ct. 15`, both in No. 16A451).
16. `mcp_courtlistener_search(type="o", court="scotus", docket_number="16A450")`
    - Returned 0 results.
17. `mcp_courtlistener_search(type="o", court="scotus", q="Alabama "stay of execution"", filed_after="2016-01-01", filed_before="2016-11-04")`
    - Returned 5 opinions (*Dunn v. Madison*, *Brooks v. Dunn*, *Arthur v. Dunn*, *Foster v. Chatman*, *Williams v. Pennsylvania*).
18. `mcp_courtlistener_search(type="o", court="scotus", q="Hurst v. Florida Alabama", filed_after="2016-01-01", filed_before="2016-11-04")`
    - Returned 4 opinions (*Kirksey v. Alabama*, *Russell v. Alabama*, *Johnson v. Alabama*, *Wimbley v. Alabama*).
19. `mcp_courtlistener_search(type="o", court="ala", q="Hurst v. Florida", filed_after="2016-01-01", filed_before="2016-11-04")`
    - Returned 1 opinion (*Ex parte Bohannon*, 222 So. 3d 525 (Ala. Sept. 30, 2016)).
20. `mcp_courtlistener_search(type="o", court="alacrimapp", q="Hurst v. Florida", filed_after="2016-01-01", filed_before="2016-11-04")`
    - Returned 3 opinions (*Ex parte State*, *Reeves v. State*, *Horton v. State*).
