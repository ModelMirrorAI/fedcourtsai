# Retrieval Log — `scotus/9026000272` / `evt-petition-disposition`

Mode: `forward` (`decided_before: null`, `cutoff: null`; petition distributed November 17, 2026 for the future December 4, 2026 Conference).

## 1. Local CLI & Corpus Queries (`uv run fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 9026000272 --event evt-petition-disposition --role predictor && uv run fedcourts query --help`
   - Transfer line: none (path resolution and CLI `--help`).
   - Returned cell paths and query flag documentation.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15`
   - `ranged corpus reads: 44 GET(s), 11403264 byte(s)`
   - Returned 15 recent 2020s granted SCOTUS rows (including OT2026 SG cert grants `26-239` *Mullin v. RAICES*, `26-204` *DOJ v. McNutt*, `25-1103` *U.S. DOGE Service*, `25-1343` *Blanche v. Ozurumba*, and `26-104` *Rhoney v. Barbosa da Cunha*).
3. `uv run fedcourts query --court scotus --docket-number 24A1030`
   - `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned *United States, et al. v. Commander Emily Shilling, et al.*, No. 24A1030 (`disposition: "granted"`, `interim_reading: "granted"`, decided `2025-05-06`).
4. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 15`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   - Returned 15 recent November 2026 denied SCOTUS cert petitions and applications.
5. `uv run fedcourts query --court scotus --citation "146 S. Ct. 2356" --citation "146 S. Ct. 2121" --citation "605 U.S. 495"`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows with CLI note explaining that only 195 SCOTUS rows in the corpus store parallel reporter citations.
6. `uv run fedcourts open-events --court scotus --limit 30`
   - Failed with CLI usage error (`No such option: --limit`, exit code 2).
7. `uv run fedcourts open-events --court scotus | head -n 40`
   - Printed `Name the case by exactly one of --docket and --docket-number.` (no transfer line).
8. `uv run fedcourts query --court scotus --era 2020s --include-open --include-applications --limit 25 | grep -i -E "talbott|shilling|hegseth|26-272|26A" || true`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned recent November 16–20, 2026 `26A` applications (`26A686`–`26A722`), confirming no emergency stay application had been docketed in *Talbott* following the Nov. 17 mandate order.
9. `uv run fedcourts query --court scotus --era 2020s --include-open --include-applications --limit 300 2>&1 | grep -i -E "ranged corpus|talbott|shilling|hegseth|26-272" || true`
   - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Confirmed no additional companion/cross-petition or stay application under *Talbott*, *Shilling*, or *Hegseth* in the top 300 2020s rows.
10. `uv run fedcourts query --court scotus --docket-number 26A416`
    - `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned *Donald J. Trump, et al. v. Alishea Sophia Kingdom, et al.*, No. 26A416 (`disposition: "denied"`, `interim_reading: "denied"`, decided `2026-10-21`), cited in Judge Wilkins's Nov. 17, 2026 statement.
11. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 100` (piped to Python filter for SG-as-petitioner cert rows)
    - `ranged corpus reads: 57 GET(s), 14942208 byte(s)`
    - Returned 23 granted SG/federal-party cert petitions from OT2025–OT2026 with their `distribution_count` values (`26-239`, `26-204`, `25-1103`, `25-1343`, `26-104`, `26-426`, `25-886`, `25-767`, `25-966`, `25-1083`, `25-1084`, `25-579`, `25-406`, `25-429`, `25-365`, `25-5`, `24-1234`, `25-332`, etc.).
12. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 100` (piped to Python filter for SG-as-petitioner cert rows)
    - `ranged corpus reads: 18 GET(s), 4587520 byte(s)`
    - Identified *Donald J. Trump, et al. v. Neeta Thakur, et al.*, No. 26-210 (`distribution_count: 1`, `date_cert_denied: "2026-11-16"`, `ca9` No. 25-4249).
13. `uv run fedcourts query --court scotus --docket-number 26-210`
    - `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
    - Returned full row for *Trump v. Thakur*, No. 26-210.
14. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 500` (piped to Python filter for SG-as-petitioner cert rows)
    - `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
    - Confirmed `26-210` (*Trump v. Thakur*) as the sole SG-filed cert denial in that window.
15. `uv run fedcourts query --court ca9 --docket-number 25-4249`
    - `ranged corpus reads: 135 GET(s), 35389440 byte(s)`
    - Returned stub `ca9` docket row (`ca9/70763252`).
16. `uv run fedcourts query --court cadc --docket-number 25-5243`
    - `ranged corpus reads: 67 GET(s), 17563648 byte(s)`
    - Returned `cadc` row (`cadc/70702469`, decided `2026-04-24`).
17. `uv run fedcourts query --court scotus --docket-number 25-1083`
    - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
    - Returned *Markwayne Mullin v. Dahlia Doe*, No. 25-1083 (`merits_decided: "2026-06-25"`, `merits_judgment: "reversed"`).
18. `uv run fedcourts query --court scotus --era 2020s --limit 1000`
    - Failed validation on `--limit 1000` (no rows returned; no transfer line).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="d", court="dcd", case_name="Talbott v. United States")`
   - Failed: HTTP 429 rate limit (`Expected available in 15 seconds`).
2. `mcp_courtlistener_search(type="d", docket_number="25-2039")`
   - Failed: HTTP 429 rate limit (`Expected available in 15 seconds`).
3. `mcp_courtlistener_search(type="d", court=["dcd", "cadc"], case_name="Talbott", num_results=10)`
   - Succeeded (`count: 3`): returned `cadc` docket `69800554` (*Nicolas Talbott v. USA*, No. 25-5087, filed `2025-03-27`, terminated `2026-06-01`).
4. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69800554, "order_by": "-date_filed", ...})` (attempt 1)
   - Failed: HTTP 429 rate limit (`Expected available in 10 seconds`).
5. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"docket_number": "1:25-cv-00240", ...})`
   - Failed: HTTP 429 rate limit (`Expected available in 10 seconds`).
6. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69800554, "order_by": "-date_filed", ...})` (attempt 2)
   - Failed: HTTP 429 rate limit (`Expected available in 1 second`).
7. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69800554, "order_by": "-date_filed", ...}, num_results=15)` (attempt 3)
   - Succeeded (`count: 140`): returned post-judgment entries in D.C. Cir. No. 25-5087, including the **November 17, 2026** Per Curiam Order (`id: 485933414`) denying appellants' motion to stay issuance of the mandate (with an attached statement by Judge Wilkins and noted dissent by Judge Walker) and the **November 17, 2026** Mandate Issued entry.
8. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry": 485933414, ...})`
   - Succeeded: returned `recap_document_id: 501824094` (`page_count: 8`, `is_available: true`, "Per Curiam Order Filed (Merits Panel)").
9. `mcp_courtlistener_read_document(recap_document_id=501824094)`
   - Succeeded (`13,718` chars): read the full November 17, 2026 D.C. Circuit Per Curiam Order denying stay of mandate and Judge Wilkins's 7-page statement addressing equities, *United States v. Shilling*, *Trump v. Kingdom* (No. 26A416), and *West Virginia v. B.P.J.*, 146 S. Ct. 2356 (2026).
10. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"court": "ca9", "docket_number": "25-2039", ...})`
    - Succeeded: returned `ca9` docket `69811434` (*Shilling, et al. v. Trump, et al.*, No. 25-2039, `date_terminated: null`).
11. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69811434, ...})` (attempt 1)
    - Failed: HTTP 429 rate limit (`Expected available in 33 seconds`).
12. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"court": "dcd", "docket_number": "1:25-cv-00240", ...})` (attempt 1)
    - Failed: HTTP 429 rate limit (`Expected available in 32 seconds`).
13. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69811434, "order_by": "-date_filed", ...}, num_results=10)` (attempt 2)
    - Succeeded (`count: 101`): returned Ninth Circuit entries in *Shilling* through **November 6, 2026** (`id: 484719100`), showing that the panel (Callahan, Christen, Hurwitz) **vacated** the November 10, 2026 oral argument and ordered supplemental briefs by November 16, 2026 on district-court notices concerning the *Shilling* plaintiffs' military status and dismissals.
14. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"court": "dcd", "docket_number": "1:25-cv-00240", ...})` (attempt 2)
    - Succeeded: returned `dcd` docket `69583866` (*TALBOTT v. TRUMP*, No. 1:25-cv-00240, `date_terminated: null`).
15. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69583866, ...})` (attempt 1)
    - Failed: HTTP 429 rate limit (`Expected available in 2 seconds`).
16. `mcp_courtlistener_search(type="o", docket_number="25-4249")`
    - Failed: HTTP 429 rate limit (`Expected available in 1 second`).
17. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69583866, "order_by": "-date_filed", ...}, num_results=15)` (attempt 2)
    - Succeeded (`count: 346`): returned D.D.C. entries in *Talbott v. Trump* through **November 20, 2026**, including Judge Reyes's Nov. 14 Minute Order noting withdrawal of the government's summary-judgment notice, Nov. 16 Minute Order denying the government's protective-order motion on deliberative-process privilege and ordering Army Secretary Daniel P. Driscoll's deposition, Nov. 19 docketing of the D.C. Circuit's mandate (`Dkt. 185`), and Nov. 20 Pretrial Statement and Motions in Limine (`Dkt. 186–192`).
18. `mcp_courtlistener_search(type="o", court="ca9", case_name="Thakur")`
    - Succeeded (`count: 3`): returned *Thakur v. Trump*, No. 25-4249 (`cluster_id: 10864473`, filed `2026-05-26`).
19. `mcp_courtlistener_search(type="o", docket_number="25-5243")`
    - Succeeded (`count: 4`): returned *RAICES v. Mullin*, D.C. Cir. No. 25-5243 (`cluster_id: 10847684`, filed `2026-04-24`).
20. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10864473, ...})` (attempt 1)
    - Failed: HTTP 429 rate limit (`Expected available in 22 seconds`).
21. `mcp_courtlistener_search(type="o", court=["cadc", "scotus"], case_name="Kingdom")`
    - Failed: HTTP 429 rate limit (`Expected available in 22 seconds`).
22. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10864473, ...})` (attempt 2)
    - Succeeded: returned `opinion_id: 11331917` for *Thakur v. Trump*.
23. `mcp_courtlistener_search(type="o", court="scotus", citation="146 S. Ct. 2356")`
    - Succeeded (`count: 0`): parallel citation not yet indexed on cluster.
24. `mcp_courtlistener_read_document(opinion_id=11331917, chunk_index=0, chunk_size=5000)` and `chunk_index=1`
    - Succeeded (2 calls): read summary and opening of *Thakur v. Trump* (9th Cir. May 26, 2026), confirming the Ninth Circuit sided with the government on the Tucker Act/APA Form Termination Class and affirmed only a First Amendment viewpoint-discrimination preliminary injunction as to UC research grants.
25. `mcp_courtlistener_search(type="o", court="scotus", case_name="B.P.J.")`
    - Succeeded (`count: 6`): returned *West Virginia v. B. P. J.* (`cluster_id: 10882186`, filed `2026-06-30`).
26. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10882186, ...})`
    - Succeeded: returned `opinion_id: 11349709`.
27. `mcp_courtlistener_read_document(opinion_id=11349709, chunk_index=0, chunk_size=8000)` and `mcp_courtlistener_search_document(opinion_id=11349709, query="transgender classification")`
    - Returned `"error": "No text is available for this document"` on both calls (relying instead on the verified passages quoted in `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, and Judge Wilkins's Nov. 17, 2026 statement).
28. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10847684, ...})` and `mcp_courtlistener_read_document(opinion_id=11315059, chunk_index=0, chunk_size=4000)`
    - First call returned `opinion_id: 11315059` (*RAICES v. Mullin*); second call returned `"error": "No text is available for this document"`.

## 3. Web Retrieval (`web_fetch` and `google_web_search`)

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-272.html`
   - Confirmed live SCOTUS docket entries matched the provisioned `2026-11-23.json` snapshot verbatim through the November 17, 2026 distribution for the December 4, 2026 Conference, with no subsequent filings or orders.
2. `google_web_search(query=""Shilling v. Trump" "25-2039" Ninth Circuit 2026")`
   - Returned a synthesized grounding summary that erroneously claimed the Ninth Circuit issued a per curiam opinion on October 30, 2026 in *Shilling*. I treated that synthesis as untrusted, checked primary CourtListener RECAP docket `69811434`, and confirmed the synthesis was hallucinated (*Shilling* remains open with oral argument vacated on November 6, 2026). Disregarded completely. No forecasts surfaced.
3. `google_web_search(query=""Talbott v. United States" "25-5087" mandate OR "25-cv-00240" trial 2026")`
   - Returned lower-court procedural summary referencing the Nov. 17, 2026 mandate in No. 25-5087 and Nov. 16, 2026 D.D.C. discovery order ahead of the Jan. 4, 2027 bench trial (note: its summary table misstated the SCOTUS cert filing date as Aug. 19 rather than Aug. 27, 2026); all relied-upon facts were independently verified from primary CourtListener RECAP dockets `69800554` and `69583866` and `recap_document_id: 501824094`. No forecasts surfaced.
