# Retrieval Log

Mode: `forward` (`DECIDED_BEFORE` unset; no web searches attempted).

## Local Corpus CLI (`uv run fedcourts ...`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000446" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Result: Resolved cell paths (`case_id scotus/9026000446`, `corpus corpus/corpus.db`, `event .../event.yaml`) and listed `fedcourts query` options.
2. `uv run fedcourts query --court scotus --judge Pillard --judge Wilkins --judge Katsas --limit 15`
   - `ranged corpus reads: 744 GET(s), 194904064 byte(s)`
   - Result: 0 rows returned (SCOTUS rows do not populate circuit panel judges in `--judge`).
3. `uv run fedcourts query --court scotus --citation "411 U.S. 792" --limit 15`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: 0 rows returned (note printed that `--citation` matches a case's own parallel cites across 195 SCOTUS rows, not cited authorities).
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - `ranged corpus reads: 3 GET(s), 786432 byte(s)`
   - Result: 10 recent granted SCOTUS rows returned (including paid cert grants showing typical distribution counts of 2–5 and amicus participation, e.g., `25-1408`, `25-944`, `26-239`, `26-12`, `26-204`).
5. `uv run fedcourts query --court scotus --attorney "Roman Martinez" --era 2020s --limit 25`
   - Result: Failed with CLI usage error (`Exit Code: 2`, `No such option: --attorney`).
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 10 recent denied SCOTUS rows returned for comparison of distribution counts and salience scores.
7. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 5 recent GVR SCOTUS rows returned (`25-442`, `25-1348`, `26-5123`, `25-1269`, `25-1367`).

## CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="McCreight v. AuburnBank", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
   - Result: `count: 0` (caption spells `Auburn Bank` as two words).
2. `mcp_courtlistener_search(type="o", case_name="Bart v. Golub", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
   - Result: `count: 1` — *Bart v. Golub Corp.*, 96 F.4th 566 (2d Cir. 2024) (`cluster_id: 9487869`, `opinion_id: 9954482`).
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Ames v. Ohio Department of Youth Services", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
   - Result: `count: 2` — *Ames v. Ohio Department of Youth Services*, 605 U.S. 303 (2025) (`cluster_id: 10599010` / `10776847`, `opinion_id: 11243434`).
4. `mcp_courtlistener_search(type="o", court="scotus", case_name="Hittle v. City of Stockton", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
   - Result: `count: 0`.
5. `mcp_courtlistener_read_document(opinion_id=11243434, chunk_index=[0, 1])`
   - Result: Read syllabus and opening of *Ames v. Ohio Department of Youth Services*, 605 U.S. 303 (2025).
6. `mcp_courtlistener_read_document(opinion_id=9954482, chunk_index=[0, 1, 2])`
   - Result: Read opening and factual/procedural background of *Bart v. Golub Corp.*, 96 F.4th 566 (2d Cir. 2024).
7. `mcp_courtlistener_search(type="o", citation="117 F.4th 1322", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
   - Result: `count: 1` — *Julia McCreight v. Auburn Bank*, 117 F.4th 1322 (11th Cir. 2024) (`cluster_id: 10121845`, `opinion_id: 10588458`).
8. `mcp_courtlistener_search(type="o", court=["scotus", "cadc", "ca11", "ca7", "ca5"], q='"2000e-16" "Babb" "2000e-2(m)"', fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
   - Result: `count: 0`.
9. `mcp_courtlistener_search(type="o", court="scotus", q='"Hittle" "McDonnell Douglas"', fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
   - Result: `count: 2` — slip and preliminary-print versions of *Ames v. Ohio Department of Youth Services*, 605 U.S. 303 (2025), citing Justice Thomas's dissent from denial of cert in *Hittle v. City of Stockton*.
10. `mcp_courtlistener_read_document(opinion_id=11243434, chunk_index=[2, 3, 4, 5, 6, 7, 8, 9, 10])`
    - Result: Read remainder of *Ames*, including footnote 2 of the Court's opinion and Justice Thomas's concurrence joined by Justice Gorsuch (605 U.S. at 314–26).
11. `mcp_courtlistener_read_document(opinion_id=9954482, chunk_index=[3, 4, 5, 6, 7, 8])`
    - Result: Read remainder of *Bart v. Golub Corp.*, 96 F.4th 566 (2d Cir. 2024), verifying that summary-judgment forfeiture was not at issue and the plaintiff had direct gender remarks and argued mixed-motive causation.
12. `mcp_courtlistener_search_document(opinion_id=10588458, query="motivating")`
    - Result: `match_count: 0` in *McCreight*.
13. `mcp_courtlistener_search_document(opinion_id=10588458, query="mixed-motive")`
    - Result: `match_count: 39` (`shown: 20`) in *McCreight v. Auburn Bank*, 117 F.4th 1322 (11th Cir. 2024).
14. `mcp_courtlistener_search(type="o", citation="679 F.3d 840", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 1` — *Ponce v. Billington*, 679 F.3d 840 (D.C. Cir. 2012) (`opinion_id: 800130`).
15. `mcp_courtlistener_search(type="o", citation="902 F.3d 309", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 2`, including *Edward Ford, Jr. v. Charles Massarone*, 902 F.3d 309 (D.C. Cir. 2018) (`opinion_id: 4309574`).
16. `mcp_courtlistener_search(type="o", court=["scotus", "cadc", "ca11", "ca7", "ca5", "ca4"], q='"2000e-16(a)" "Babb"', fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id"])`
    - Result: `count: 4` (*Jane DiCocco v. Merrick Garland*, 4th Cir.).
17. `mcp_courtlistener_read_document(opinion_id=10588458, chunk_index=[3, 4])`
    - Result: Read *McCreight v. Auburn Bank*, 117 F.4th at 1331–34, holding there is no "magic words" rule for mixed-motive claims at summary judgment, only a basic party-presentation obligation to "connect the dots."
18. `mcp_courtlistener_read_document(opinion_id=800130, chunk_index=[0, 1])`
    - Result: Read chunks 0–1 of *Ponce v. Billington*, 679 F.3d 840 (D.C. Cir. 2012).
19. `mcp_courtlistener_read_document(opinion_id=4309574, chunk_index=[0, 1])`
    - Result: Read chunks 0–1 of *Ford v. Massarone*, 902 F.3d 309 (D.C. Cir. 2018).
20. `mcp_courtlistener_search(type="o", citation="992 F.3d 1193", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 1` — *Noris Babb v. Secretary, Department of Veterans Affairs*, 992 F.3d 1193 (11th Cir. 2021) (`opinion_id: 4673790`).
21. `mcp_courtlistener_search(type="o", citation="42 F.4th 638", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 1` — *Alice Huff v. Pete Buttigieg*, 42 F.4th 638 (7th Cir. 2022) (`opinion_id: 7374880`).
22. `mcp_courtlistener_read_document(opinion_id=4673790, chunk_index=[0, 1, 2])`
    - Result: Read *Babb v. Secretary, Department of Veterans Affairs*, 992 F.3d 1193, 1198–1205 (11th Cir. 2021), holding *Babb v. Wilkie* governs federal-sector Title VII claims under 42 U.S.C. § 2000e-16(a) rather than § 2000e-2(m).
23. `mcp_courtlistener_read_document(opinion_id=7374880, chunk_index=[0, 1])`
    - Result: Read *Huff v. Buttigieg*, 42 F.4th 638 (7th Cir. 2022) (applying *Babb* to federal-sector Title VII).
24. `mcp_courtlistener_read_document(opinion_id=800130, chunk_index=[2, 3])`
    - Result: Read remainder of *Ponce v. Billington*, 679 F.3d 840 (D.C. Cir. 2012).
25. `mcp_courtlistener_read_document(opinion_id=4309574, chunk_index=[2, 3])`
    - Result: Read chunks 2–3 of *Ford v. Massarone*, 902 F.3d 309 (D.C. Cir. 2018).
26. `mcp_courtlistener_search(type="o", citation="350 F.3d 1061", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 1` — *Stegall v. Citadel Broadcasting Co.*, 350 F.3d 1061 (9th Cir. 2003) (`opinion_id: 9496566`).
27. `mcp_courtlistener_search_document(opinion_id=9496566, query="mixed")`
    - Result: `match_count: 14` in *Stegall*, confirming plaintiff's record and brief supported both pretext and mixed-motives and survived under either theory.
28. `mcp_courtlistener_search(type="o", citation="424 F.3d 1027", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 1` — *Dominguez-Curry v. Nevada Transportation Department*, 424 F.3d 1027 (9th Cir. 2005) (`opinion_id: 9498405`).
29. `mcp_courtlistener_search(type="o", citation="527 F.3d 1340", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 1` — *Ginger v. District of Columbia*, 527 F.3d 1340 (D.C. Cir. 2008) (`opinion_id: 187191`).
30. `mcp_courtlistener_search(type="o", court="cadc", q='"Babb v. Wilkie"', fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 7`, including *Jennifer Seed v. EPA*, 100 F.4th 257 (D.C. Cir. 2024) (`opinion_id: 9966581`).
31. `mcp_courtlistener_read_document(opinion_id=9966581, chunk_index=[0, 1])`
    - Result: Read *Seed v. EPA*, 100 F.4th 257 (D.C. Cir. 2024), on Article III redressability limits for former federal employees when damages and reinstatement are unavailable.
32. `mcp_courtlistener_read_document(opinion_id=187191, chunk_index=[0, 1])`
    - Result: Read chunks 0–1 of *Ginger v. District of Columbia*, 527 F.3d 1340 (D.C. Cir. 2008).
33. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2025-06-06", q='"2000e-2(m)" OR "McDonnell Douglas"', fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id"])`
    - Result: `count: 0`.
34. `mcp_courtlistener_read_document(opinion_id=187191, chunk_index=2)`
    - Result: Read chunk 2 of *Ginger v. District of Columbia*, 527 F.3d at 1345–46.
35. `mcp_courtlistener_search_document(opinion_id=9498405, query="motivating")`
    - Result: `match_count: 9` in *Dominguez-Curry*.
36. `mcp_courtlistener_read_document(opinion_id=9498405, chunk_index=[7, 8])`
    - Result: Read footnotes 4–9 of *Dominguez-Curry*, 424 F.3d at 1036–42.
37. `mcp_courtlistener_search(type="o", court="scotus", q='"City of Stockton" "McDonnell Douglas"', fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
    - Result: `count: 2` (both printings of *Ames*).
38. `mcp_courtlistener_search(type="r", court="dcd", docket_number="1:19-cv-02058", fields=["caseName", "docketNumber", "docket_id", "assignedTo", "dateFiled"])`
    - Result: `count: 1` (*Simmons v. U.S. Department of State*, confirming Tarquinii's district court case had a different docket number).
39. `mcp_courtlistener_search(type="r", court="dcd", party_name="Tarquinii", fields=["caseName", "docketNumber", "docket_id", "assignedTo", "dateFiled"])`
    - Result: `count: 1` — *Tarquinii v. Harker*, No. `1:21-cv-01567` (filed 2021-06-07, assigned to Judge Rudolph Contreras before reassignment to Judge Jia M. Cobb, confirming Justice Jackson did not preside over the district court action).
