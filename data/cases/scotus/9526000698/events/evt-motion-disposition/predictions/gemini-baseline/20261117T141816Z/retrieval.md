# Retrieval Log (`scotus/9526000698` — `evt-motion-disposition` — `20261117T141816Z`)

Mode: `forward` (`decided_before: null`). No lookup of `26A698`'s own Supreme Court disposition, subsequent history, or external forecasts was attempted.

## 1. `fedcourts` Corpus CLI Lookups

1. `uv run fedcourts paths --court "scotus" --docket "9526000698" --event "evt-motion-disposition" --role predictor` and `uv run fedcourts query --help`
   - Transfer line: none (CLI path resolution and help inspection).
   - Returned: resolved case/event paths and structured `fedcourts query` flag specification.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Stderr transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Returned: 10 recent OT2026 SCOTUS cert denials decided `2026-11-16`.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr transfer line: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
   - Returned: 10 recent OT2026 SCOTUS grants, including 3 substantive interim application grants (`26A560` *Mullin v. Friends of the Ruidosa Church*, `26A512` *Scanlan v. Coalition for Open Democracy*, and `26A476` *FCC v. Brown*), all federal or state government applicants with `referred_to_court: true` and responses filed.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --limit 10`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: 10 recent OT2026 cert denials from `2026-11-16`.
5. `uv run fedcourts query --court scotus --originating-court cadc --era 2020s --disposition denied --include-applications --limit 25`
   - Result: Failed (exit code 2) — `No such option: --originating-court`.
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --limit 100`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: 100 cert denials from the `2026-11-16` order list (`0` application rows in top 100).
7. `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --decided-before 2026-11-15 --limit 50`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: 50 SCOTUS denials decided before `2026-11-15`, including 4 substantive interim application denials: `26A680` (*Dowden v. Deutsche Bank National Trust Company, as Trustee*, decided `2026-11-13`, `referred_to_court: false`, `response_requested: false`, `amicus_briefs: 0`), `26A661` (*Pavatt v. Oklahoma*, capital prisoner, decided `2026-11-12`, `referred_to_court: true`, `response_requested: false`), `26A658` (*Schultz v. Gold*, decided `2026-11-11`, `referred_to_court: false`, `response_requested: false`), and `26A657` (*Schultz v. McCarthy*, CA4 / Chief Justice Roberts, decided `2026-11-10`, `referred_to_court: false`, `response_requested: false`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="r", court=["cadc", "dcd"], party_name="Simpkins", fields=["caseName", "docketNumber", "court_id", "dateFiled", "dateTerminated", "docket_id"], num_results=10)`
   - Returned: 32 RECAP matches (10 shown), including D.D.C. dockets `1:26-cv-00304` (`SIMPKINS v. STATE OF TENNESSEE`, `docket_id=72231859`, filed `2026-01-20`), `1:26-cv-00310` (`SIMPKINS v. CAESAR`, `docket_id=72232400`, filed `2026-01-31`), and `1:25-cv-04566` (`SIMPKINS v. STATE OF TENNESSEE`, `docket_id=72108735`, filed `2025-12-22`).
2. `mcp_courtlistener_search(type="o", court=["cadc", "dcd"], q="Simpkins", fields=["caseName", "docketNumber", "court_id", "dateFiled", "citation", "cluster_id"], num_results=10)`
   - Returned: 496 matches (10 shown), identifying opinion cluster `10774655` (`Simpkins v. State of Tennessee`, D.D.C. `Civil Action No. 2025-4566`, filed `2026-01-14`).
3. `mcp_courtlistener_analyze_citations(text="Oviedo v. WMATA, 948 F.3d 386 (D.C. Cir. 2020); Whitley v. Warden, 401 U.S. 560 (1971); Caperton v. A.T. Massey Coal Co., 556 U.S. 868 (2009); Steel Co. v. Citizens for a Better Environment, 523 U.S. 83 (1998); Younger v. Harris, 401 U.S. 37 (1971); Sprint Communications, Inc. v. Jacobs, 571 U.S. 69 (2013); Nieves v. Bartlett, 587 U.S. 391 (2019); Shapiro v. McManus, 577 U.S. 39 (2015).")`
   - Returned: 8 of 8 citations verified; confirmed canonical spellings for OCR-affected citations in `application.txt` (*Henry Oviedo v. WMATA*, 948 F.3d 386; *Whiteley v. Warden, Wyoming State Penitentiary*, 401 U.S. 560).
4. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 72231859, "fields": ["entry_number", "date_filed", "description"]}, num_results=30)`
   - Returned: 30 docket entries in D.D.C. `1:26-cv-00304` (`SIMPKINS v. STATE OF TENNESSEE`), showing Judge Amir H. Ali's Feb. 24, 2026 order denying TRO/PI (ECF 16) and subsequent entries through Oct. 14, 2026 (ECF 30).
5. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 72232400, "fields": ["entry_number", "date_filed", "description"]}, num_results=20)`
   - Returned: 5 docket entries in D.D.C. `1:26-cv-00310` (`SIMPKINS v. CAESAR`), confirming it was a separate civil action filed `2026-01-31` without payment of the $405 filing fee or an IFP application.
6. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10774655, "fields": ["id", "author_str", "type"]}, num_results=5)`
   - Returned: `opinion_id=11241240` for `Simpkins v. State of Tennessee`, No. `25-04566` (D.D.C. Jan. 14, 2026).
7. `mcp_courtlistener_search(type="o", court="cadc", docket_number="26-7061", fields=["caseName", "docketNumber", "dateFiled", "docket_id", "cluster_id"], num_results=10)`
   - Returned: 0 results.
8. `mcp_courtlistener_search(type="o", court="cadc", docket_number="26-7016", fields=["caseName", "docketNumber", "dateFiled", "docket_id", "cluster_id"], num_results=10)`
   - Returned: 0 results.
9. `mcp_courtlistener_read_document(opinion_id=11241240)`
   - Returned: Full text (15,590 chars) of Judge Amir H. Ali's Jan. 14, 2026 Memorandum Opinion dismissing `Simpkins v. State of Tennessee`, No. `25-04566` (D.D.C.), under FRCP 8(a), *Rooker-Feldman*, lack of jurisdiction over Middle District of Tennessee proceedings, and *Younger* abstention.
10. `mcp_courtlistener_call_endpoint(endpoint_id="recap-documents", query={"docket_entry__docket": 72231859, "fields": ["id", "document_number", "description", "is_available"]}, num_results=25)`
    - Returned: 25 RECAP document metadata rows for D.D.C. `1:26-cv-00304`, confirming exact filing dates and descriptions for the dismissal orders (`2026-03-04`, ECF 21/22), post-judgment Motion for Three-Judge Court and Vacatur (`2026-03-19`, ECF 25), denial order (`2026-03-24`), Notice of Appeal (`2026-04-30`, ECF 27), and USCA Mandate (`2026-10-14`, ECF 30).
11. `mcp_courtlistener_search(type="o", court="dcd", docket_number="26-cv-00304", fields=["caseName", "docketNumber", "dateFiled", "cluster_id"], num_results=5)`
    - Returned: 0 results.
12. `mcp_courtlistener_search(type="o", court="dcd", docket_number="2026-0304", fields=["caseName", "docketNumber", "dateFiled", "cluster_id"], num_results=5)`
    - Returned: 0 results.
13. `mcp_courtlistener_search(type="r", court=["tnmd", "ca6"], party_name="Simpkins", fields=["caseName", "docketNumber", "court_id", "dateFiled", "dateTerminated", "docket_id"], num_results=10)`
    - Returned: 0 results.
14. `mcp_courtlistener_search(type="o", court=["tnmd", "ca6"], q=""David M. Simpkins" OR "Sally E. Simpkins"", fields=["caseName", "docketNumber", "court_id", "dateFiled", "citation", "cluster_id"], num_results=10)`
    - Returned: 0 results.

## 3. Web Searches

None attempted.
