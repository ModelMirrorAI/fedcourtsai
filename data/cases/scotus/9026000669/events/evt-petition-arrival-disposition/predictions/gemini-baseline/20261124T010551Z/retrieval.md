# Retrieval Log — `scotus/9026000669` (`evt-petition-arrival-disposition`)

Mode: `forward` (`cutoff = 2026-11-24`). All retrieval targeted related litigation (*Department of Homeland Security v. D.V.D.*, No. 26-426 / No. 26A406; linked extension application No. 26A302) and general SCOTUS corpus priors; no third-party forecasts were sought or encountered.

## 1. `fedcourts` CLI Calls
1. `uv run fedcourts paths --court "scotus" --docket "9026000669" --event "evt-petition-arrival-disposition" --role predictor && uv run fedcourts query --help`
   - No ranged corpus reads; returned cell paths and `fedcourts query` flag documentation.
2. `uv run fedcourts query --court scotus --docket-number 26-426`
   - `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Returned `scotus/9026000426` (*Department of Homeland Security, et al. v. D. V. D., et al.*), showing `disposition: "granted"`, `date_cert_granted: "2026-09-29"`, `originating_court: "ca1"`, `originating_docket_number: "26-1212"`, and counsel/amicus metadata.
3. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 15`
   - `ranged corpus reads: 44 GET(s), 11403264 byte(s)`
   - Returned 15 recent 2020s SCOTUS GVR rows to inspect `distribution_count` and hold-petition resolution patterns.
4. `uv run fedcourts query --court scotus --attorney "Prelogar" --disposition gvr --limit 20`
   - Failed with CLI usage error (`No such option: --attorney`); no corpus reads executed.
5. `uv run fedcourts query --court scotus --attorney "Sauer" --limit 25`
   - Failed with CLI usage error (`No such option: --attorney`); no corpus reads executed.
6. `uv run fedcourts query --court scotus --docket-number 26A406 --include-applications --include-open`
   - `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
   - Returned `scotus/9526000406` (*Department of Homeland Security, et al. v. D. V. D., et al.*), substantive stay application filed `2026-09-24` and granted `2026-09-29`.
7. `uv run fedcourts query --court scotus --disposition gvr --decided-before 2026 --era 2020s --limit 25`
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Returned prior-Term GVR rows confirming multiple distributions (`distribution_count >= 2`) on held/relisted petitions.
8. `uv run fedcourts query --court scotus --docket-number 26A302 --include-applications --include-open`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned linked extension application `scotus/9526000302` (*United States v. Jorge Felix Ibarra-Perez*), decided `2026-10-15`, confirming respondent's counsel of record (`Trina A. Realmuto`).
9. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 10`
   - `ranged corpus reads: 4 GET(s), 917504 byte(s)`
   - Returned recent SCOTUS denial rows confirming `distribution_count` conventions on resolved cert petitions vs. applications.

## 2. CourtListener MCP Calls
1. `mcp_courtlistener_search(court="ca1", docket_number="26-1212", type="o", fields=["caseName", "citation", "cluster_id", "dateFiled", "docketNumber", "opinions"])` (Attempt 1)
   - Returned HTTP 429 rate-limit error (`Expected available in 4 seconds`).
2. `mcp_courtlistener_search(court="ca1", docket_number="26-1212", type="o", fields=["caseName", "citation", "cluster_id", "dateFiled", "docketNumber", "opinions"])` (Attempt 2)
   - Succeeded (`query_id: ded68368`); returned 1 result: *D.V.D. v. U.S. Department of Homeland Security*, `cluster_id: 10976939`, `opinion_id: 11444581`, `dateFiled: "2026-09-18"`.
3. `mcp_courtlistener_search_document(opinion_id=11444581, query="Ibarra-Perez", snippet_size=500)` and `mcp_courtlistener_search_document(opinion_id=11444581, query="1252(g)", snippet_size=400)` (Attempt 1, parallel)
   - Both returned HTTP 429 rate-limit error (`Expected available in 2 seconds`).
4. `mcp_courtlistener_search_document(opinion_id=11444581, query="Ibarra-Perez", snippet_size=700)` (Attempt 2)
   - Succeeded; returned 2 matches showing the First Circuit in *D.V.D.* expressly cited *Ibarra-Perez v. United States*, 154 F.4th 989, 997 (9th Cir. 2025), in holding that 8 U.S.C. § 1252(g) did not bar the class's third-country removal claims.
5. `mcp_courtlistener_read_document(opinion_id=11444581, chunk_index=[4, 5], chunk_size=8000)`
   - Succeeded; returned the First Circuit's discussion of DHS's 8 U.S.C. § 1252(g) jurisdictional defense in *D.V.D.*
6. `mcp_courtlistener_read_document(opinion_id=11444581, chunk_index=[0, 1, 6, 7], chunk_size=8000)`
   - Succeeded; returned caption, panel, counsel, background, and remaining jurisdictional analysis in *D.V.D.*

## 3. Web Fetches (`web_fetch`)
1. `web_fetch` on official Supreme Court docket pages `https://www.supremecourt.gov/docket/docketfiles/html/public/26-426.html` and `https://www.supremecourt.gov/docket/docketfiles/html/public/26-669.html`
   - Returned official docket proceedings and oral-argument schedule (Wednesday, December 9, 2026) for *DHS v. D.V.D.*, No. 26-426, and confirmed No. 26-669's docketing entries matched the provisioned `2026-11-24.json` snapshot (newly docketed Nov. 23, 2026, response due Dec. 23, 2026).
2. `web_fetch` on `https://www.supremecourt.gov/qp/26-00426qp.pdf` and `https://www.supremecourt.gov/docket/docketfiles/html/public/26-426.html`
   - Returned the four Questions Presented directed by the Court in No. 26-426 (including Question 1: *"Whether the district court had jurisdiction over Respondents' claims"*) and the full text of the September 29, 2026 order granting a stay (with Justices Sotomayor, Kagan, and Jackson noting they would deny the stay) and granting certiorari.
3. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-426.html` requesting brief PDF URLs and summaries of the Table of Contents / Summary of Argument of Petitioners' and Respondents' merits briefs
   - Returned empty output (large PDF brief text not extracted).
