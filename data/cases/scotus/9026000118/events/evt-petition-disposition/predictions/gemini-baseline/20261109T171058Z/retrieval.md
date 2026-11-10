# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-116`
   - Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned 1 row: `scotus/9026000116` (*Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.*), `distribution_count: 3`, `distributed_for_conference: 2026-11-13`.
2. `uv run fedcourts query --court scotus --docket-number 26-117`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 1 row: `scotus/9026000117` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*), `distribution_count: 3`, `distributed_for_conference: 2026-11-13`.
3. `uv run fedcourts query --court scotus --citation "599 U.S. 1" --limit 5`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (`note:` line indicated sparse citation coverage).
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 24 GET(s), 6291456 byte(s)`
   - Returned 5 rows (`25-1408`, `26A512`, `26-12`, `26-204`, `26A476`).
5. `uv run fedcourts query --court scotus --docket-number 25-273`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: `scotus/73275215` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*, No. 25-273), `date_cert_granted: 2026-05-11`, `disposition: gvr`.
6. `uv run fedcourts query --court scotus --docket-number 25-272`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 1 row: `scotus/73275212` (*Andy Luu Tran v. Herbert Jacobs*, unrelated).
7. `uv run fedcourts query --court scotus --docket-number 25-274`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 1 row: `scotus/73275213` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*, No. 25-274), `date_cert_granted: 2026-05-11`, `disposition: gvr`.
8. `uv run fedcourts query --court scotus --docket-number 25A1314`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 1 row: `scotus/73431862` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*, No. 25A1314), `date_decided: 2026-06-02`, `disposition: granted`.
9. `uv run fedcourts query --court scotus --docket-number 25A1315`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 1 row: `scotus/73500399` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*, No. 25A1315), `date_decided: 2026-06-02`, `disposition: granted`.
10. `uv run fedcourts query --court scotus --docket-number 25-275`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned 1 row: `scotus/73275214` (*Clifford James Frost, Jr. v. Dana Nessel*, unrelated).
11. `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversed --limit 10`
    - Failed with usage error (`Unknown disposition 'summary-reversed'; choose one of: granted, denied, granted-in-part, gvr, summary-reversal, dismissed, withdrawn, other`).
12. `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 10`
    - Transfer: `ranged corpus reads: 1039 GET(s), 272367616 byte(s)`
    - Returned 0 rows.
13. `uv run fedcourts query --court scotus --era 2020s --disposition dismissed --limit 10`
    - Transfer: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
    - Returned 8 rows (`26-2`, `26-346`, `26-5347`, `25-1427`, `26-5287`, `26-5309`, `25-7548`, `25-7666`).
14. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned 10 rows (`25-1269`, `25-1367`, `25-7569`, `26-139`, `26-5216`, `25-901`, `25-918`, `25-7462`, `25-7532`, etc.).
15. `uv run fedcourts query --court scotus --era 2020s --disposition other --limit 10`
    - Transfer: `ranged corpus reads: 1030 GET(s), 270008320 byte(s)`
    - Returned 0 rows.
16. `uv run fedcourts query --court scotus --docket-number 26-116 --full`
    - Transfer: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
    - Returned 1 row (`scotus/9026000116`).
17. `uv run fedcourts query --court scotus --docket-number 26-117 --full`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned 1 row (`scotus/9026000117`).
18. `uv run fedcourts query --court scotus --docket-number 26-118 --full`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned 1 row (`scotus/9026000118`).
19. `uv run fedcourts query --court scotus --era 2020s --party "League of United Latin American Citizens" --limit 10`
    - Failed with usage error (`No such option: --party`).
20. `uv run fedcourts query --court scotus --docket-number 25-248`
    - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned 1 row: `scotus/73213319` (*District of Columbia v. R.W.*, No. 25-248), `disposition: granted`, `merits_judgment: reversed`.
21. `uv run fedcourts query --court scotus --docket-number 24-109`
    - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned 1 row: `scotus/69779623` (*Louisiana v. Phillip Callais, et al.*, No. 24-109), `merits_decided: 2026-04-29`, `merits_judgment: affirmed`.
22. `uv run fedcourts query --court scotus --docket-number 24-110`
    - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned 1 row: `scotus/72483576` (*Press Robinson, et al. v. Phillip Callais, et al.*, No. 24-110), `merits_decided: 2026-04-29`, `merits_judgment: affirmed`.
23. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 30`
    - Transfer: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
    - Returned 19 rows.
24. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 25`
    - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned 19 rows.
25. `uv run fedcourts query --court scotus --disposition summary-reversal --limit 5`
    - Transfer: `ranged corpus reads: 1011 GET(s), 265027584 byte(s)`
    - Returned 0 rows.
26. `uv run fedcourts query --court scotus --disposition other --limit 5`
    - Transfer: `ranged corpus reads: 364 GET(s), 95420416 byte(s)`
    - Returned 5 historical rows.
27. `uv run fedcourts query --court scotus --disposition granted-in-part --limit 5`
    - Transfer: `ranged corpus reads: 1070 GET(s), 280494080 byte(s)`
    - Returned 0 rows.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Allen v. Milligan", filed_after="2026-01-01", num_results=10)`
   - Returned 1 cluster (`Allen v. Milligan`, 146 S. Ct. 1377, decided 2026-06-02, `opinion_id=11336479`, `docket_number="25A1314"`).
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Louisiana v. Callais", filed_after="2026-01-01", num_results=10)`
   - Returned 2 clusters (`Louisiana v. Callais`, decided 2026-04-29, `opinion_id=11320154`, and revisions 2026-05-04, `opinion_id=11317641`).
3. `mcp_courtlistener_read_document(opinion_id=11336479)`
   - Returned full text (52,827 chars) of the June 2, 2026 stay order, Justice Kavanaugh's concurrence, Justice Thomas's concurrence, and Justice Sotomayor's dissent in *Allen v. Milligan*, 146 S. Ct. 1377 (2026).
4. `mcp_courtlistener_search(type="rd", case_name="Singleton v. Allen", filed_after="2026-05-01", num_results=20)`
   - Returned 0 results.
5. `mcp_courtlistener_search(type="rd", case_name="Milligan v. Allen", filed_after="2026-05-01", num_results=20)`
   - Returned 0 results.
6. `mcp_courtlistener_search(type="o", court="scotus", case_name="Abbott v. League of United Latin American Citizens", filed_after="2025-01-01", num_results=10)`
   - Returned 0 results.
7. `mcp_courtlistener_search(type="d", docket_number="2:21-cv-01291", num_results=20)`
   - Returned 13 dockets, including `docket_id=60607496` (*Singleton v. Allen*, N.D. Ala. No. 2:21-cv-01291-AMM).
8. `mcp_courtlistener_search(type="d", docket_number="2:21-cv-01530", num_results=20)`
   - Returned 11 dockets, including `docket_id=61494291` (*Milligan v. Allen*, N.D. Ala. No. 2:21-cv-01530-AMM).
9. `mcp_courtlistener_search(type="o", court="scotus", case_name="Abbott", filed_after="2025-10-01", num_results=10)`
   - Returned 0 results.
10. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 60607496, "order_by": "-date_filed", "fields": ["id", "entry_number", "date_filed", "description"]}, num_results=30)`
    - Returned 30 recent docket entries in *Singleton v. Allen* (N.D. Ala. No. 2:21-cv-01291) from May 19, 2026 to August 27, 2026.
11. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 61494291, "order_by": "-date_filed", "fields": ["id", "entry_number", "date_filed", "description"]}, num_results=30)`
    - Returned 30 recent docket entries in *Milligan v. Allen* (N.D. Ala. No. 2:21-cv-01530) from May 8, 2026 to August 27, 2026.
12. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry": 483044181, ...})`
    - Returned metadata for *Singleton* Doc. 373 (`is_available: false`).
13. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry": 483044177, ...})`
    - Returned metadata for *Singleton* Doc. 369 (`is_available: false`).
14. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry": 483044178, ...})`
    - Returned metadata for *Singleton* Doc. 370 (`is_available: false`).
15. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry": 483044182, ...})`
    - Returned metadata for *Singleton* Doc. 374 (`is_available: false`).
16. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2026-04-20", filed_before="2026-05-15", num_results=20)`
    - Returned 8 SCOTUS opinions from late April to mid-May 2026.
17. `mcp_courtlistener_read_document(opinion_id=11320154, chunk_index=[0, 1], chunk_size=8000)`
    - Read chunks 0 and 1 of *Louisiana v. Callais* (`opinion_id=11320154`).
18. `mcp_courtlistener_read_document(opinion_id=11320154, chunk_index=2, chunk_size=8000)`
    - Read chunk 2 of *Louisiana v. Callais* (`opinion_id=11320154`).
19. `mcp_courtlistener_search(type="o", court="scotus", q="Callais", filed_after="2026-04-24", filed_before="2026-05-15")`
    - Returned 2 *Callais* clusters.
20. `mcp_courtlistener_search(type="d", court="scotus", docket_number="26-118")`, `docket_number="26-117"`, `docket_number="26-116"`, and `party_name="Singleton"`
    - All returned 0 results (SCOTUS docket coverage on CourtListener is thin).
21. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry__docket": 60607496, "is_available": true, "order_by": "-id", ...}, num_results=30)`
    - Returned available RECAP documents in *Singleton v. Allen* (`60607496`), including Doc. 357 (`recap_document_id=480176543`).
22. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry__docket": 61494291, "is_available": true, "order_by": "-id", ...}, num_results=30)`
    - Returned available RECAP documents in *Milligan v. Allen* (`61494291`), including Doc. 544 (`recap_document_id=492999516`) and Doc. 545 (`recap_document_id=492999517`).
23. `mcp_courtlistener_read_document(recap_document_id=492999516)`
    - Read *Milligan* Doc. 544 (July 20, 2026 three-judge district court Order staying trial-court discovery and post-judgment motions pending resolution of the Supreme Court appeals).
24. `mcp_courtlistener_read_document(recap_document_id=492999517)`
    - Read *Milligan* Doc. 545 (Supreme Court notice of docketing for No. 26-117).
25. `mcp_courtlistener_read_document(recap_document_id=480176543)`
    - Read *Singleton* Doc. 357 (May 15, 2026 Motion for a Preliminary Injunction filed by the *Singleton* Plaintiffs on remand after *Callais*).
26. `mcp_courtlistener_search(type="o", court="scotus", q="League of United Latin American Citizens", filed_after="2026-04-01", filed_before="2026-06-01")` and `filed_after="2026-04-20", filed_before="2026-05-05"`
    - Returned *Callais* and other late-April 2026 SCOTUS opinions.
