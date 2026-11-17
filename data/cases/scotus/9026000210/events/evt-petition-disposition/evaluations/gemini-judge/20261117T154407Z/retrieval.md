# Evaluator Retrieval Log — `scotus/9026000210` / `evt-petition-disposition` (`20261117T154407Z`)

## 1. Local CLI & Statpack Reconstruction (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 9026000210 --event evt-petition-disposition --role evaluator`
   - Local path helper (no corpus transfer).
2. `uv run fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
   - Reconstructed prediction-time statpack build `dedb32b153e6` (`sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`) shared by all three candidates (`run_id = 20261102T130502Z`); no corpus transfer.
3. `uv run fedcourts query --court scotus --docket-number 26-210`
   - Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Verified stored corpus metadata for `scotus/9026000210` (`disposition = "denied"`, `date_cert_denied = "2026-11-16"`, `distribution_count = 1`, `has_opinion = false`).

## 2. CourtListener MCP Lookups (Citation & Lower-Court Docket Audit)

1. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", num_results=45, query={"docket": 70459259, "fields": ["id", "entry_number", "date_filed", "description"], "order_by": "-date_filed"})`
   - Inspected N.D. Cal. docket entries in *Thakur v. Trump*, No. 3:25-cv-04737-RFL, including Entry 228 (Sept. 1, 2026 partial stay order) and Entry 246 (Oct. 13, 2026 supplemental briefing order).
2. `mcp_courtlistener_search(type="o", citation="179 F.4th 1042", fields=["caseName", "court", "dateFiled", "citation"])`
   - Returned `count: 0` (checking `gemini-baseline`'s cited reporter string `179 F.4th 1042`).
3. `mcp_courtlistener_search(type="o", citation="176 F.4th 1187", fields=["caseName", "court", "dateFiled", "citation", "judge"])`
   - Returned `count: 0` (recent F.4th reporter pagination not yet indexed on cluster search).
4. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry": 476537220, "fields": ["id", "document_number", "attachment_number", "description", "is_available"]})`
   - Resolved `recap_document_id = 492102631` for N.D. Cal. Entry 228.
5. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry": 481409413, "fields": ["id", "document_number", "attachment_number", "description", "is_available"]})`
   - Resolved `recap_document_id = 497150947` for N.D. Cal. Entry 246.
6. `mcp_courtlistener_search(type="r", court="ca2", docket_number="26-1829", fields=["caseName", "court", "dateFiled", "docketNumber"])`
   - Verified *American Council of Learned Societies v. English*, 2d Cir. No. 26-1829 (filed `2026-07-08`).
7. `mcp_courtlistener_search(type="o", court="ca9", case_name="Thakur v. Trump", fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "judge"])`
   - Verified the three Ninth Circuit decisions in No. 25-4249 (`2025-08-21`, `2025-12-23`, `2026-05-26`).
8. `mcp_courtlistener_read_document(recap_document_id=492102631)`
   - Read N.D. Cal. ECF No. 228 (Sept. 1, 2026 Stipulation and Order staying summary judgment and class certification briefing on all claims except Plaintiffs' DOE Equal Protection claim pending Supreme Court disposition).
9. `mcp_courtlistener_read_document(recap_document_id=497150947)`
   - Read N.D. Cal. ECF No. 246 (Oct. 13, 2026 Order requesting supplemental briefing solely on Plaintiffs' Equal Protection claim against DOE).
10. `mcp_courtlistener_search(type="o", court="ca9", case_name="Thakur v. Trump", fields=["caseName", "dateFiled", "cluster_id", "opinions"])`
    - Retrieved cluster/opinion IDs for the Ninth Circuit decisions in *Thakur v. Trump*.
11. `mcp_courtlistener_read_document(opinion_id=11124665, chunk_index=0, chunk_size=2000)`
    - Checked caption header of the Aug. 21, 2025 Ninth Circuit stay opinion.
12. `mcp_courtlistener_search(type="d", court="ca2", docket_number="26-1829", fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
    - Resolved `docket_id = 73588928` (`dateTerminated = null`) for 2d Cir. No. 26-1829.
13. `mcp_courtlistener_search(type="d", court="ca2", docket_number="25-2481", fields=["caseName", "docketNumber", "docket_id", "dateFiled", "dateTerminated"])`
    - Checked `25-2481` (`count: 0` on docket search).
14. `mcp_courtlistener_analyze_citations(text=...)`
    - Verified 27 case citations cited across the candidates' `reasoning.md` files against CourtListener's citation-lookup database.
15. `mcp_courtlistener_read_document(opinion_id=11124665, chunk_index=1, chunk_size=2500)`
    - Confirmed the Aug. 21, 2025 Ninth Circuit stay panel was also Judges Paez, Christen, and Desai (Judge Gould never sat on *Thakur v. Trump*).
16. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", num_results=15, query={"docket": 73588928, "fields": ["id", "entry_number", "date_filed", "description"], "order_by": "-date_filed"})`
    - Verified active briefing status in *American Council of Learned Societies v. English*, 2d Cir. No. 26-1829.
17. `mcp_courtlistener_read_document(opinion_id=11252285, chunk_index=0, chunk_size=2500)`
    - Verified caption, date (`2026-02-06`), and panel/disposition of *Nat'l Ass'n of Diversity Officers in Higher Educ. v. Trump* (4th Cir. No. 25-1189).

## 3. Web Searches

None.
