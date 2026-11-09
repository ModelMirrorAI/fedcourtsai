# Retrieval Log

## 1. Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-1206`
   - Stderr transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned `scotus/73281690` (*Wes Moore, Governor of Maryland, et al. v. Susannah Warner Kipke, et al.*, No. 25-1206), Maryland's cross-petition from the same Fourth Circuit judgment, filed April 22, 2026 and dismissed August 13, 2026 (`disposition: "dismissed"`).
2. `uv run fedcourts query --court scotus --docket-number 25-541`
   - Stderr transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/73278986` (*Benjamin Schoenthal, et al. v. Kwame Raoul, Attorney General of Illinois, et al.*, No. 25-541), a Second Amendment challenge to Illinois's public-transit firearm ban with the same Counsel of Record (David H. Thompson), denied April 6, 2026 after 4 distributions (`distribution_count: 4`, `salience_score: 0.4042`).
3. `uv run fedcourts query --court scotus --citation "597 U.S. 1" --limit 20`
   - Stderr transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned 0 rows with coverage note (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all, and the column holds a case's OWN parallel cites`).
4. `uv run fedcourts query --court ca4 --judge Gregory --judge Diaz --judge Agee --limit 10`
   - Stderr transfer line: `ranged corpus reads: 93 GET(s), 24379392 byte(s)`
   - Result: Returned 0 rows (circuit judge lists are withheld on the bulk circuit slice).
5. `uv run fedcourts query --court scotus --originating-court ca4 --era 2020s --limit 25`
   - Result: CLI usage error (`No such option: --originating-court`).
6. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 30`
   - Stderr transfer line: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned 30 recent 2020s SCOTUS dockets (resolved and open).
7. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 25`
   - Stderr transfer line: `ranged corpus reads: 41 GET(s), 10682368 byte(s)`
   - Result: Returned 25 granted 2020s SCOTUS dockets, including Second Amendment grants *Cutberto Viramontes, et al. v. Cook County, Illinois, et al.* (`scotus/73275645`, No. 25-238, granted June 30, 2026) and *Eddie Grant, Jr., et al. v. Ronnell Higgins, et al.* (`scotus/73279088`, No. 25-566, granted June 30, 2026), and recent Fourth Circuit grants.
8. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 25`
   - Stderr transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)` (warm cache from prior call in combined shell command)
   - Result: Returned 25 GVR dispositions in 2020s SCOTUS dockets.
9. `uv run fedcourts query --court scotus --docket-number 25-1324`
   - Stderr transfer line: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Result: Returned the corpus metadata row for `scotus/73500225` (*Novotny v. Moore*, No. 25-1324, open, `distribution_count: 5`).
10. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 40`
    - Stderr transfer line: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
    - Result: Returned 40 recent cert denials from the November 9, 2026 order list.
11. `uv run fedcourts query --court scotus --counsel-of-record "David H. Thompson" --include-open --limit 25` (and parallel calls with `--counsel-of-record`)
    - Result: CLI usage error (`No such option: --counsel-of-record`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Wolford v. Lopez"`)
   - Result: Returned 1 cluster (`cluster_id=10880241`, `opinion_id=11347760`, *Wolford v. Lopez*, 609 U.S. ___, decided June 25, 2026, Docket No. 24-1046).
2. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `case_name="Frey v. City of New York"`)
   - Result: 0 results.
3. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `case_name="Christian v. James"`)
   - Result: 0 results.
4. `mcp_courtlistener_search` (`type="o"`, `court=["scotus", "ca3"]`, `case_name="Koons"`)
   - Result: Returned 4 Third Circuit clusters, including *Ronald Koons v. Attorney General New Jersey*, `cluster_id=10673136`, decided September 17, 2025 (Nos. 23-1900, 23-2043).
5. `mcp_courtlistener_read_document` (`opinion_id=11347760`, `chunk_index=0`, `chunk_size=8000`) and (`chunk_index=[1, 2]`, `chunk_size=8000`)
   - Result: Read syllabus and opening sections of *Wolford v. Lopez*, 609 U.S. ___ (June 25, 2026) (Roberts, C.J., for a 6–3 Court; Barrett, J., concurring, joined as to Part II-B by Thomas and Gorsuch, JJ.).
6. `mcp_courtlistener_search_document` (`opinion_id=11347760`, `query="sensitive place"`), (`query="BARRETT, J., concurring"`), and (`query="1868"`)
   - Result: Retrieved snippets from *Wolford v. Lopez* addressing the sensitive-places doctrine and Justice Barrett's concurrence discussing 1791 Founding-era versus 1868 Reconstruction-era historical evidence.
7. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `filed_after="2025-10-01"`, `q='"Second Amendment" OR "sensitive places" OR "Bruen"'`) and (`q="Koons OR Frey OR Antonyuk OR Schoenthal OR Novotny OR Kipke"`)
   - Result: 0 SCOTUS docket results (consistent with thin SCOTUS docket coverage on CourtListener).
8. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2024-01-01"`, `q='"Second Amendment" OR "Bruen" OR "Rahimi"'`)
   - Result: Returned 39 Supreme Court opinions citing *Bruen* or *Rahimi* since 2024, including *United States v. Rahimi* (`cluster_id=10600058`) and *Wolford v. Lopez* (`cluster_id=10880241`).
9. `mcp_courtlistener_read_document` (`opinion_id=11243977`, `chunk_index=[18, 19, 20, 21, 22]`, `chunk_size=8000`)
   - Result: Returned range error (`document has 2 chunk(s) of 8000 characters each`), consistent with `documents.json` noting that CourtListener's extracted text for the Fourth Circuit opinion was incomplete and the pipeline fetched the PDF directly.
