# Retrieval Log

## 1. `fedcourts` Corpus Queries

1. `uv run fedcourts query --court scotus --q "First Amendment viewpoint discrimination grant termination Finley Rust" --limit 10`
   - Result: Failed with usage error (`No such option: --q`; `fedcourts query` accepts structured filters only, not free-text search).
2. `uv run fedcourts query --court scotus --q "Trump" --limit 15`
   - Result: Failed with usage error (`No such option: --q`).
3. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 25`
   - Transfer: `ranged corpus reads: 16 GET(s), 4194304 byte(s)`
   - Result: Returned 25 recent SCOTUS rows in the 2020s (including resolved OT2025/OT2026 petitions and applications).
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 25`
   - Transfer: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
   - Result: Returned 25 granted SCOTUS petitions/applications in the 2020s, including recent SG grants (*DOJ v. McNutt*, No. 26-204; *U.S. DOGE Service v. U.S. District Court*, No. 25-1103; *Blanche v. Ozurumba*, No. 25-1343; *Trump v. California*, No. 26A124; *National Park Service v. National Trust for Historic Preservation*, No. 26A203; *FCC v. Brown*, No. 26A476).
5. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 15`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 15 GVR dispositions from OT2025/OT2026 (including *Mullin v. National TPS Alliance*, No. 26-48).
6. `uv run fedcourts query --court scotus --docket-number 25A103 --include-applications --include-open`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned *National Institutes of Health, et al. v. American Public Health Association, et al.* (No. 25A103, decided 2025-08-21, disposition recorded as `denied` in part / granted in part in corpus).
7. `uv run fedcourts query --court scotus --docket-number 24A966 --include-applications --include-open`
   - Transfer: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned *Donald J. Trump, President of the United States, et al. v. Gwynne A. Wilcox, et al.* (No. 24A966, decided 2025-05-22, `granted`).
8. `uv run fedcourts query --court scotus --attorney "D. John Sauer" --include-open --limit 50`
   - Result: Failed with usage error (`No such option: --attorney`).
9. `uv run fedcourts query --court scotus --docket-number 26-210 --include-open`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned the open corpus row for `scotus/9026000210` (*Donald J. Trump, President of the United States, et al. v. Neeta Thakur, et al.*, `distribution_count = 1`, `distributed_for_conference = 2026-11-13`, `salience_score = 0.0248`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="American Council of Learned Societies", fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "status"])`
   - Result: `count: 0` (no published appellate opinion yet in *American Council of Learned Societies v. McDonald*, 2d Cir. No. 25-2481).
2. `mcp_courtlistener_search(type="r", case_name="American Council of Learned Societies", fields=["caseName", "court", "dateFiled", "docketNumber"])`
   - Result: `count: 5`, including Second Circuit docket *American Council of Learned Societies v. McDonald* (No. 25-2481, filed 2025-10-15) and S.D.N.Y. docket (1:25-cv-03657).
3. `mcp_courtlistener_search(type="o", q='"Finley" "viewpoint" grant terminate', filed_after="2025-01-01", fields=["caseName", "court", "dateFiled", "docketNumber", "citation"])`
   - Result: `count: 13`, including *Thakur v. Trump* (9th Cir. No. 25-4249, filed 2026-05-26) and related district court decisions (*Vera Institute of Justice v. DOJ*, *American Bar Association v. DOJ*, *Climate United Fund v. Citibank*, *Rhode Island Latino Arts v. NEH*).
4. `mcp_courtlistener_search(type="o", q='"Thakur v. Trump"', filed_after="2025-01-01", fields=["caseName", "court", "dateFiled", "docketNumber", "citation"])`
   - Result: `count: 7` (the Ninth Circuit opinion in *Thakur v. Trump* and district/circuit decisions citing it).
5. `mcp_courtlistener_search(type="o", q='"Executive Order 14151" "First Amendment"', filed_after="2025-01-01", fields=["caseName", "court", "dateFiled", "docketNumber", "citation"])`
   - Result: `count: 4` (district court opinions in *Mid-Atlantic Equity Consortium v. Dept. of Education*, *National Urban League v. Trump*, *Chicago Women in Trades v. Trump*, and *Northeast Organic Farming Ass'n v. USDA*).
6. `mcp_courtlistener_search(type="o", case_name="National Association of Diversity Officers", fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "id"])`
   - Result: `count: 0` (caption abbreviated in CourtListener as `Natl. Assoc. of Diversity Officers`).
7. `mcp_courtlistener_search(type="o", court="ca4", q='"National Association of Diversity Officers" OR "14151" OR "14173"', filed_after="2025-01-01", fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "id", "cluster_id"])`
   - Result: `count: 2` (*John Doe 1 v. ODNI*, cluster 10814215; *The Sustainability Institute v. Donald Trump*, cluster 10778864).
8. `mcp_courtlistener_search(type="o", q='"American Public Health Association" "National Institutes of Health"', filed_after="2025-01-01", fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "id", "cluster_id"])`
   - Result: `count: 17`, including *Natl. Assoc. of Diversity Officers in Higher Edu. v. Donald Trump* (4th Cir., cluster 10785644, filed 2026-02-06) and *Fairfax County School Board v. Linda McMahon* (4th Cir., cluster 11037105, filed 2026-10-15).
9. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10785644, fields=["id", "case_name", "date_filed", "sub_opinions", "judges"])`
   - Result: Returned cluster metadata for *Natl. Assoc. of Diversity Officers in Higher Edu. v. Donald Trump* (Opinion ID 11252285, filed 2026-02-06).
10. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10778864, fields=["id", "case_name", "date_filed", "sub_opinions", "judges"])`
    - Result: Returned cluster metadata for *The Sustainability Institute v. Donald Trump* (Opinion IDs 11244704, 11245474, filed 2026-01-21).
11. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=11037105, fields=["id", "case_name", "date_filed", "sub_opinions", "judges"])`
    - Result: Returned cluster metadata for *Fairfax County School Board v. Linda McMahon* (Opinion ID 11504800, filed 2026-10-15).
12. `mcp_courtlistener_search(type="o", court="ca2", q='"Finley" OR "viewpoint" OR "Humanities" OR "Thakur"', filed_after="2025-01-01", fields=["caseName", "court", "dateFiled", "docketNumber", "cluster_id"])`
    - Result: `count: 15`, none involving *American Council of Learned Societies v. McDonald* (confirming no Second Circuit opinion has issued yet).
13. `mcp_courtlistener_read_document(opinion_id=11252285, chunk_index=0)`
    - Result: Read chunk 0 of the Fourth Circuit's opinion in *NADOHE v. Trump* (No. 25-1189, Feb. 6, 2026).
14. `mcp_courtlistener_read_document(opinion_id=11244704, chunk_index=0)`
    - Result: Returned `"error": "No text is available for this document."`
15. `mcp_courtlistener_read_document(opinion_id=11252285, chunk_index=[1, 2, 3])`
    - Result: Read chunks 1–3 of *NADOHE v. Trump* (standing and ripeness analysis).
16. `mcp_courtlistener_read_document(opinion_id=11252285, chunk_index=[4, 5, 6])`
    - Result: Read chunks 4–6 of *NADOHE v. Trump* (Fifth Amendment facial vagueness challenge to the Termination Provision and First Amendment facial challenge to the Certification Provision).
17. `mcp_courtlistener_read_document(opinion_id=11504800, chunk_index=[0, 1])`
    - Result: Read chunks 0–1 of the Fourth Circuit's opinion in *Fairfax County School Board v. McMahon* (No. 25-1969, Oct. 15, 2026).
18. `mcp_courtlistener_read_document(opinion_id=11504800, chunk_index=[2, 3, 4, 5])`
    - Result: Read chunks 2–5 of *Fairfax County School Board v. McMahon* (distinguishing *Sustainability Institute*, *NIH v. APHA*, and *Department of Education v. California*).
19. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"court": "ca2", "docket_number": "25-2481"})`
    - Result: Returned 0 results.
20. `mcp_courtlistener_search(type="o", citation="145 S. Ct. 2658", fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "cluster_id"])`
    - Result: Returned 0 results.
21. `mcp_courtlistener_search(type="o", docket_number="25A103", fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "cluster_id"])`
    - Result: Returned 0 results.
22. `mcp_courtlistener_search(type="o", court="scotus", q='"Department of Education v. California"', filed_after="2025-03-01", fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "cluster_id"])`
    - Result: `count: 5`, including *Department of Education v. California*, 604 U.S. 650 (cluster 10776858).
23. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10776858, fields=["id", "case_name", "date_filed", "sub_opinions", "judges"])`
    - Result: Returned cluster metadata for *Department of Education v. California* (Opinion ID 11243445).
24. `mcp_courtlistener_read_document(opinion_id=11243445)`
    - Result: Read full text of *Department of Education v. California*, 604 U.S. 650 (2025).
25. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"court": "cand", "docket_number__icontains": "4737", "fields": ["id", "case_name", "docket_number", "date_filed", "date_last_filing"]})`
    - Result: Failed validation (`docket_number__icontains` not accepted as a dict filter).
26. `mcp_courtlistener_search(type="r", court="cand", docket_number="4737", fields=["caseName", "docketNumber", "docket_id", "dateFiled"])`
    - Result: Found *Thakur v. Trump*, N.D. Cal. No. 3:25-cv-04737 (`docket_id = 70459259`).
27. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", num_results=30, query={"docket": 70459259, "order_by": "-entry_number", "fields": ["id", "entry_number", "date_filed", "description"]})`
    - Result: Returned 30 unnumbered minute entries on the N.D. Cal. docket.
28. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", num_results=30, query={"docket": 70459259, "order_by": "-date_filed", "fields": ["id", "entry_number", "date_filed", "description"]})`
    - Result: Returned the 30 most recent docket entries (through Oct. 27, 2026, Entry 250) in *Thakur v. Trump*, showing summary judgment briefing completed, EPA class settlement preliminarily approved on Oct. 1, 2026 (final approval hearing set for Dec. 10, 2026), and summary judgment hearing set for Nov. 17, 2026.
29. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry": 481409413, "fields": ["id", "document_number", "attachment_number", "description", "is_available"]})`
    - Result: Returned `recap_document_id = 497150947` for Entry 246 (Order Requesting Supplemental Briefing, Oct. 13, 2026).
30. `mcp_courtlistener_read_document(recap_document_id=497150947)`
    - Result: Read Judge Lin's Oct. 13, 2026 Order Requesting Supplemental Briefing on plaintiffs' Equal Protection summary judgment motion against DOE.
31. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", num_results=30, query={"docket": 70459259, "entry_number": 210, "fields": ["id", "entry_number", "date_filed", "description"]})`
    - Result: Returned Entry 210 (Plaintiffs' Motion for Summary Judgment and Motion to Certify Class, filed July 15, 2026).

## 3. Web Searches

None attempted.
