# Retrieval Log — `scotus/9526000714` (`evt-motion-disposition`, `20261119T141840Z`)

Mode: `forward` (`decided_before: null`). Every corpus CLI call, CourtListener MCP lookup, and web fetch attempted during this run is logged below.

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9526000714" --event "evt-motion-disposition" --role predictor` and `uv run fedcourts query --help`
   - Result: Resolved `case_id` (`scotus/9526000714`), `corpus` (`corpus/corpus.db`), and `event` path; printed `fedcourts query` flag documentation (no corpus transfer line).
2. `uv run fedcourts query --court scotus --docket-number 24A1059`
   - Stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned `scotus/72415675`, *Kristi Noem v. National TPS Alliance* (`24A1059`), filed `2025-05-01`, decided `2025-05-19`, `disposition: "granted"`, `interim_reading: "granted"`, `response_requested: true` (`2025-05-01`), `referred_to_court: true`, `amicus_briefs: 4`.
3. `uv run fedcourts query --court scotus --docket-number 25A326`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/71543224`, *Kristi Noem v. National TPS Alliance* (`25A326`), filed `2025-09-19`, decided `2025-10-03`, `disposition: "granted"`, `interim_reading: "granted"`, `response_requested: true` (`2025-09-22`), `referred_to_court: true`, `amicus_briefs: 4`.
4. `uv run fedcourts query --court scotus --docket-number 26-48`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/9026000048`, *Markwayne Mullin v. National TPS Alliance* (`26-48`), filed `2026-07-13`, cert granted / GVR `2026-10-05` (`disposition: "gvr"`).
5. `uv run fedcourts query --court scotus --docket-number 26A406`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/9526000406`, *Department of Homeland Security v. D.V.D.* (`26A406`), filed `2026-09-24`, decided `2026-09-29`, `disposition: "granted"`, `interim_reading: "granted"`, `response_requested: true`, `referred_to_court: true`, `amicus_briefs: 2`.
6. `uv run fedcourts query --court scotus --era 2020s --disposition withdrawn --limit 10`
   - Stderr: `ranged corpus reads: 261 GET(s), 68419584 byte(s)`
   - Result: Returned 10 withdrawn 2020s SCOTUS applications (`26A273`, `26A297` *USPS v. California*, `25A964`, `25A539` *Rollins v. Rhode Island State Council of Churches*, `25A227` *Trump v. Global Health Council*, `24A1106` *Trump v. AFGE*, `23A60`, `22A974`, `21A230`, `20A85`), showing `interim_reading: "withdrawn"` and ladder flags (`referred_to_court`, `response_requested`, `amicus_briefs`).
7. `uv run fedcourts query --court scotus --era 2020s --disposition dismissed --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 dismissed 2020s SCOTUS dockets (`26A397`, `26-119`, `26-96`, `25-1195`, `25-7773`, `25-1208`, `25A81`, `24-1102`, `24-7252`, `24-924`).
8. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent OT2026 granted SCOTUS dockets/applications (`25-944`, `26-239`, `26A560` *Mullin v. Friends of the Ruidosa Church*, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476` *FCC v. Brown*, `25-1103`, `25-7026`).
9. `uv run fedcourts query --court scotus --era 2020s --disposition denied --attorney "D. John Sauer" --include-applications --limit 15`
   - Failed (exit code 2): `No such option: --attorney` (printed `fedcourts query` option help).
10. `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --limit 15`
    - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: Returned 15 recent OT2026 denied SCOTUS applications and cert petitions (`26A698`, `26A711`, `25-1238`, `25-1240`, `25-1303`, `25-1324`, `25-7485`, `25-7562`, `25-7667`, `26-4`, `26-62`, `26-100`, `26-120`, `26-127`, `26-210`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Mullin v. Doe", fields=[...])`
   - Returned 1 cluster (`cluster_id: 10880242`, `opinion_id: 11347761`), *Mullin v. Doe*, No. 25-1083, decided `2026-06-25`.
2. `mcp_courtlistener_search(type="r", court="ca9", docket_number="25-5724", fields=[...])`
   - Returned 1 RECAP docket (`docket_id: 71328538`), *National TPS Alliance, et al. v. Mullin, et al.*, No. `25-5724` (9th Cir.).
3. `mcp_courtlistener_read_document(opinion_id=11347761, chunk_index=0, chunk_size=10000)` and `mcp_courtlistener_read_document(opinion_id=11347761, chunk_index=[0, 12], chunk_size=5000)` and `mcp_courtlistener_read_document(opinion_id=11347761, chunk_index=1, chunk_size=5000)`
   - Read syllabus, lineup, and holdings of *Mullin v. Doe*, 609 U.S. 324 (2026) (6–3; Alito, J., for the Court; Thomas, J., concurring; Kagan, J., dissenting joined by Sotomayor and Jackson, JJ.).
4. `mcp_courtlistener_search(type="o", court="scotus", case_name="National TPS Alliance", fields=[...])`
   - Returned 0 opinion results.
5. `mcp_courtlistener_search(type="o", court="scotus", case_name="Ruidosa Church", fields=[...])`
   - Returned 1 cluster (`cluster_id: 11057881`, `opinion_id: 11525671`), *Mullin v. Friends of the Ruidosa Church*, No. `26A560`, decided `2026-11-09`.
6. `mcp_courtlistener_read_document(opinion_id=11525671, chunk_index=0, chunk_size=8000)` and `mcp_courtlistener_read_document(opinion_id=11525671, chunk_index=1, chunk_size=8000)`
   - Read full per curiam stay opinion in *Mullin v. Friends of the Ruidosa Church* (`26A560`, Nov. 9, 2026; Jackson, J., noting she would deny).
7. `mcp_courtlistener_search(type="rd", court="ca9", docket_number="25-5724", order_by="entry_date_filed desc", num_results=20)` (plus follow-up `num_results=6` and `num_results=8` with `id` / `description` fields, and `description="SUPPLEMENTAL BRIEF submitted for filing by Appellant Markwayne Mullin"`)
   - Returned latest Ninth Circuit remand entries in `25-5724`, including `DE 109` (`2026-11-18 04:01 PM PT`, `id: 502048561`, granting administrative stay expiring seven days after publication of judgment), `DE 108` (`2026-11-18 12:01 PM PT`, courtesy copy of `26A714`), `DE 106` (`2026-11-10`, `id: 501495956`, Appellees' supplemental brief), and `DE 102` (`2026-11-06`, `id: 500727989`, Government's supplemental brief).
8. `mcp_courtlistener_read_document(recap_document_id=502048561)`
   - Read full text of Ninth Circuit `DE 109` (`11/18/2026`): *"Before: WARDLAW, MENDOZA, Jr., and JOHNSTONE, Circuit Judges. The Government's motion for an administrative stay that expires seven days after the publication of our judgment is GRANTED."*
9. `mcp_courtlistener_read_document(recap_document_id=501495956, chunk_index=0, chunk_size=8000)` and `mcp_courtlistener_read_document(recap_document_id=501495956, chunk_index=[1, 5], chunk_size=8000)`
   - Read Appellees' November 10, 2026 supplemental brief on remand (`DE 106`) regarding vacatur reviewability under *Mullin v. Doe* and opposition to a post-decision administrative stay.
10. `mcp_courtlistener_read_document(recap_document_id=500727989, chunk_index=0, chunk_size=8000)`
    - Read Appellants' November 6, 2026 supplemental brief (`DE 102`), including the alternative request for an order extending the administrative stay seven days after any decision in the appeals.
11. `mcp_courtlistener_search(type="o", court="scotus", docket_number="25A326")` and `mcp_courtlistener_search(type="o", court="scotus", docket_number="26A406")`
    - Returned 0 opinion-index results on both queries.
12. `mcp_courtlistener_search(type="rd", court="ca1", docket_number="26-1944")`, `mcp_courtlistener_search(type="rd", court="ca9", docket_number="25-3030")`, `mcp_courtlistener_search(type="rd", court="cadc", docket_number="25-5097")`, `mcp_courtlistener_search(type="rd", court="ca1", docket_number="26-1988")`, and `mcp_courtlistener_search(type="rd", court="ca1", docket_number="25-2089")`
    - Checked lower-court procedural context behind prior withdrawn Solicitor General applications (`26A297`, `24A1106`, `25A227`, `25A539`), confirming each followed lower-court merits vacatur, TRO expiration, or mooting legislation.
13. `mcp_courtlistener_search(type="o", court="scotus", q='"administrative stay" "application for stay"', filed_after="2021-01-01")` and `mcp_courtlistener_search(type="o", court="scotus", q='"National TPS Alliance"', filed_after="2024-01-01")`
    - Returned 0 results on the first query and 1 result (*Mullin v. Doe*, No. `25-1083`) on the second.

## 3. Web Fetches (`supremecourt.gov` Official Docket JSONs)

1. `web_fetch` of `https://www.supremecourt.gov/RSS/Cases/JSON/26A714.json`
   - Confirmed `26A714` remains pending as of November 19, 2026 with only the single November 18, 2026 submission entry to Justice Kagan (matching provisioned `snapshots/2026-11-18.json`).
2. `web_fetch` of resolved prior Supreme Court docket JSONs:
   - `https://www.supremecourt.gov/RSS/Cases/JSON/24A1059.json` (*Noem v. National TPS Alliance*: granted May 19, 2025; Jackson, J., would deny).
   - `https://www.supremecourt.gov/RSS/Cases/JSON/25A326.json` (*Noem v. National TPS Alliance*: granted Oct. 3, 2025; Sotomayor and Kagan, JJ., would deny; Jackson, J., filed a detached dissenting opinion).
   - `https://www.supremecourt.gov/RSS/Cases/JSON/26A297.json`, `https://www.supremecourt.gov/RSS/Cases/JSON/25A539.json`, and `https://www.supremecourt.gov/RSS/Cases/JSON/25A227.json` (confirming docket-entry sequence on prior Solicitor General withdrawals).
