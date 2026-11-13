# Retrieval Log

All lookups performed beyond the provisioned files in `data/cases/scotus/9026000239/record/` and committed repository files (`metrics/statpack.md`, `metrics/statpack.json`, schemas, and `config/predictors.yaml`):

## 1. `fedcourts` CLI Lookups

1. `uv run fedcourts paths --court "scotus" --docket "9026000239" --event "evt-order-judgment" --role predictor`
   - Result: Resolved `case_id` (`scotus/9026000239`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts corpus-query --help`
   - Result: Exit code 2 (`No such command 'corpus-query'`); inspected `uv run fedcourts --help` and `uv run fedcourts query --help` to confirm the subcommand spelling is `uv run fedcourts query`.
3. `uv run fedcourts query --court scotus --docket-number 26-426 --decided-before 2026-11-14`
   - Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned 1 row (`scotus/9026000426`, *Department of Homeland Security, et al. v. D. V. D., et al.*, `date_cert_granted: 2026-09-29`, `originating_court: ca1`, `originating_docket_number: 26-1212`).
4. `uv run fedcourts query --court scotus --citation "596 U.S. 543" --citation "597 U.S. 785" --citation "585 U.S. 667" --decided-before 2026-11-14`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Empty result with sparse-citation coverage note (`only 195 row(s) in scope (scotus) carry any reporter citation at all`).
5. `uv run fedcourts query --court scotus --era 2020s --decided-before 2026-11-14 --limit 15`
   - Transfer: `ranged corpus reads: 9 GET(s), 2293760 byte(s)`
   - Result: Returned 15 recent SCOTUS rows from November 2026 (including this docket's grant entry and recent cert/GVR/application dispositions).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Al Otro Lado", filed_before="2026-11-13")`
   - Result: 1 match — *Mullin v. Al Otro Lado*, `cluster_id=10880243`, `opinion_id=11347762`, filed `2026-06-25`.
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="D.V.D.", filed_before="2026-11-13")`
   - Result: Broad token match (`count=896`, unrelated slip/order entries); did not locate a merits SCOTUS opinion for *D.V.D.* (which is pending for argument Dec. 9, 2026).
3. `mcp_courtlistener_search(type="o", court="cadc", case_name="Refugee and Immigrant Center for Education and Legal Services", filed_before="2026-11-13")`
   - Result: 3 D.C. Circuit matches (including *Refugee and Immigrant Center for Education and Legal Services v. Mullin*, `cluster_id=10847540`, `opinion_id=11315059`, filed `2026-04-24`).
4. `mcp_courtlistener_read_document(opinion_id=11347762, chunk_index=[0, 1], chunk_size=8000)`
   - Result: Read syllabus of *Mullin v. Al Otro Lado* (June 25, 2026).
5. `mcp_courtlistener_read_document(opinion_id=11315059, chunk_index=[17, 18, 19, 20, 21, 22], chunk_size=8000)`
   - Result: Error (`No text is available for this document` on CourtListener's opinion endpoint; relied on provisioned `decision-below.txt`, `petition.txt`, and `brief-in-opposition.txt`).
6. `mcp_courtlistener_search(type="o", court="scotus", case_name="Trump v. Barbara", filed_before="2026-11-13")`
   - Result: 2 matches for *Trump v. Barbara* (`cluster_id=10883542`, `opinion_id=11351070`; `cluster_id=10882236`, `opinion_id=11349764`, filed `2026-06-30`).
7. `mcp_courtlistener_search(type="o", court="scotus", case_name="Trump v. CASA", filed_before="2026-11-13")`
   - Result: 5 matches, led by *Trump v. CASA, Inc.*, 606 U.S. 831 (`cluster_id=10776816`, `opinion_id=11243403`, filed `2025-06-27`).
8. `mcp_courtlistener_read_document(opinion_id=11351070, chunk_index=[0, 1], chunk_size=8000)`
   - Result: Error (`No text is available for this document` on the July 1, 2026 revisions entry).
9. `mcp_courtlistener_read_document(opinion_id=11243403, chunk_index=[0, 1], chunk_size=8000)`
   - Result: Read syllabus of *Trump v. CASA, Inc.*, 606 U.S. 831 (2025).
10. `mcp_courtlistener_search(type="o", court="scotus", case_name="Aleman Gonzalez", filed_before="2026-11-13")`
    - Result: 0 matches under `case_name="Aleman Gonzalez"` (indexed on CourtListener as *Garland v. Gonzalez*).
11. `mcp_courtlistener_search(type="o", court="scotus", case_name="Biden v. Texas", filed_before="2026-11-13")`
    - Result: 1 match — *Biden v. Texas*, 597 U.S. 785 (`cluster_id=6344019`, `opinion_id=6496704`, filed `2022-06-30`).
12. `mcp_courtlistener_search(type="o", court="ca1", q=""1252(f)(1)"", filed_after="2026-09-01", filed_before="2026-11-13")`
    - Result: 1 match — *D.V.D. v. U.S. Department of Homeland Security*, `cluster_id=10976939`, `opinion_id=11444581` (1st Cir., filed `2026-09-18`).
13. `mcp_courtlistener_read_document(opinion_id=11349764, chunk_index=[0, 1], chunk_size=8000)`
    - Result: Read syllabus of *Trump v. Barbara* (June 30, 2026).
14. `mcp_courtlistener_read_document(opinion_id=11243403, chunk_index=[2], chunk_size=8000)`
    - Result: Read conclusion of syllabus and lineup of *Trump v. CASA, Inc.*, 606 U.S. 831 (2025).
15. `mcp_courtlistener_read_document(opinion_id=6496704, chunk_index=[0, 1], chunk_size=8000)`
    - Result: Read syllabus and lineup of *Biden v. Texas*, 597 U.S. 785 (2022).
16. `mcp_courtlistener_search_document(opinion_id=11444581, query="1252(f)(1)", snippet_size=500)`
    - Result: Retrieved 8 snippets in *D.V.D. v. DHS* (1st Cir. Sept. 18, 2026) addressing § 1252(f)(1), APA vacatur, and classwide declaratory relief.
17. `mcp_courtlistener_search(type="o", court="scotus", citation="596 U.S. 543", filed_before="2026-11-13")`
    - Result: Matched *Garland v. Gonzalez*, 596 U.S. 543 (`cluster_id=6185086`, `opinion_id=6349227`, filed `2022-06-13`).
18. `mcp_courtlistener_read_document(opinion_id=11349764, chunk_index=[2], chunk_size=8000)`
    - Result: Read remainder of *Trump v. Barbara* syllabus.
19. `mcp_courtlistener_read_document(opinion_id=6349227, chunk_index=[0, 1], chunk_size=8000)`
    - Result: Read syllabus and lineup of *Garland v. Aleman Gonzalez*, 596 U.S. 543 (2022).
20. `mcp_courtlistener_search_document(opinion_id=11243403, query="Alito, J., concurring", snippet_size=1500)`
    - Result: Read Justice Alito's concurrence (joined by Justice Thomas) in *Trump v. CASA, Inc.* regarding Rule 23 class certification.
21. `mcp_courtlistener_search(type="o", court="scotus", case_name="Learning Resources", filed_before="2026-11-13")`
    - Result: 2 matches for *Learning Resources, Inc. v. Trump* (`cluster_id=10796677`, `opinion_id=11263492`, filed `2026-02-20`).
22. `mcp_courtlistener_read_document(opinion_id=11263492, chunk_index=[0, 1, 2], chunk_size=8000)`
    - Result: Read syllabus of *Learning Resources, Inc. v. Trump*, 607 U.S. 229 (2026).
23. `mcp_courtlistener_read_document(opinion_id=11347762, chunk_index=[0, 1], chunk_size=4000)`
    - Result: Read opening syllabus chunks of *Mullin v. Al Otro Lado* (2026).
24. `mcp_courtlistener_read_document(opinion_id=11347762, chunk_index=[2], chunk_size=4000)`
    - Result: Read lineup and opening opinion header of *Mullin v. Al Otro Lado* (2026).
25. `mcp_courtlistener_search(type="d", court="scotus", docket_number="26-426", filed_before="2026-11-13")`
    - Result: 0 matches (consistent with thin SCOTUS docket coverage on CourtListener).
26. `mcp_courtlistener_search_document(opinion_id=[11347762, 11349764, 11263492], query="delivered the opinion", snippet_size=450)`
    - Result: Verified exact vote lineups and separate writings in *Mullin v. Al Otro Lado* (2026), *Trump v. Barbara* (2026), and *Learning Resources, Inc. v. Trump* (2026).

## 3. Web Searches

None attempted.
