# Retrieval Log

Cell mode: `forward` (`cutoff: null`, `decided_before: null`). All lookups stayed strictly within official court dockets, prior corpus dispositions, primary circuit case law, and Senate nomination status; no external forecasts or commentary were sought or encountered.

## 1. Corpus CLI (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000304" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Resolved cell paths (`case_id: scotus/9026000304`, `corpus: corpus/corpus.db`) and CLI flag syntax; verified `$DECIDED_BEFORE` was unset (`forward` mode).
2. `uv run fedcourts query --court scotus --docket-number 26-348 2>&1`
   - `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Returned 1 row: companion petition `scotus/9026000348` (*United States v. Office of the New York State Attorney General*, docketed `2026-09-15`, `originating_court: ca2`, `originating_docket_number: 26-156`, `disposition: null`, `last_live_polled: 2026-11-16`).
3. `uv run fedcourts query --court scotus --citation "580 U.S. 288" 2>&1`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows with CLI note explaining `citations` holds a case's own parallel cites over 195 populated rows rather than a citation graph.
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10 2>&1`
   - `ranged corpus reads: 41 GET(s), 10616832 byte(s)`
   - Returned 10 recent OT2026 granted SCOTUS rows (`25-944`, `26-239`, `26A560`, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`), showing `distribution_count >= 2` across regular-conference cert grants.
5. `uv run fedcourts query --court scotus --era 2020s --disposition denied --party "United States" --limit 15 2>&1`
   - Failed (`Exit Code: 2`): `No such option: --party` (structured filter has no `--party` flag).
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 15 2>&1`
   - `ranged corpus reads: 3 GET(s), 655360 byte(s)`
   - Returned 15 recent November 2026 denied SCOTUS rows (including paid cert denials `25-1238`, `25-1240`, `25-1303`, `25-1324`, `26-4`, `26-62`, `26-100`).
7. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 40 2>&1`
   - `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
   - Returned 40 recent OT2026 granted SCOTUS rows, comparing Long Conference SG cert grants (`26-104`, `distribution_count: 1`) against October–November regular-conference SG cert grants (`25-1103`, `25-1343`, `26-204`, `26-239`, all `distribution_count: 2`).

## 2. CourtListener MCP

1. `mcp_courtlistener_search(type="o", court="ca2", case_name="Grand Jury Subpoenas", filed_after="2026-01-01", num_results=5, fields=["caseName", "citation", "dateFiled", "docketNumber", "judge", "cluster_id", "opinions"])`
   - Returned 1 result: *In Re Grand Jury Subpoenas to the Office of the New York State Attorney General*, Docket No. `26-156` (2d Cir. Aug. 27, 2026), `opinion_id: 11422024`.
2. `mcp_courtlistener_search(type="o", court=["ca4", "cadc"], q=""3345(a)(1)" OR "Federal Vacancies Reform Act"", filed_after="2025-12-01", num_results=10, ...)`
   - Failed (`HTTP 429` rate limit, 19s retry window).
3. `mcp_courtlistener_search_document(opinion_id=11422024, query="dissenting", snippet_size=400)` and `mcp_courtlistener_search(type="o", court=["ca4", "cadc"], ...)`
   - Failed (`HTTP 429` rate limit, 5s retry window).
4. `mcp_courtlistener_search_document(opinion_id=11422024, query="PARK, Circuit Judge", snippet_size=500)` and `mcp_courtlistener_search(type="o", court=["ca4", "cadc"], q=""3345" AND "Vacancies"", ...)`
   - Failed (`HTTP 429` rate limit, 1s retry window).
5. `mcp_courtlistener_search_document(opinion_id=11422024, query="dissenting", snippet_size=500)`
   - Succeeded (`match_count: 1` in `143543` chars): returned opening passage of Judge Park's dissent in *In re Grand Jury Subpoenas*, No. `26-156` (2d Cir.).
6. `mcp_courtlistener_search(type="o", court=["ca4", "cadc"], q=""3345" AND "Vacancies"", filed_after="2026-01-01", num_results=10, fields=["caseName", "citation", "dateFiled", "docketNumber", "judge"])`
   - Succeeded (`count: 0`): confirmed neither the Fourth Circuit nor the D.C. Circuit had issued a published FVRA opinion creating or resolving a split as of November 23, 2026.

## 3. Web Fetch & Web Search (`forward` mode)

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-304.html` and `https://www.supremecourt.gov/docket/docketfiles/html/public/26-348.html`
   - Returned HTML shell metadata and initial proceedings for `26-304` and `26-348`.
2. `web_fetch` on `https://www.supremecourt.gov/RSS/Cases/JSON/26-304.json` and `https://www.supremecourt.gov/RSS/Cases/JSON/26-348.json`
   - Confirmed `26-304` remains pending on its Nov. 17, 2026 distribution for the 12/4/2026 conference (matching `2026-11-23.json`) and showed `26-348` was also distributed on Nov. 17, 2026 for the 12/4/2026 conference with zero amicus briefs.
3. `web_fetch` on `https://www.supremecourt.gov/RSS/Cases/JSON/26-348.json` (PDF URL extraction) and `web_fetch` on `https://www.supremecourt.gov/DocketPDF/26/26-348/424291/20260915133157135_NYOAG%20Petition.pdf` and `https://www.supremecourt.gov/DocketPDF/26/26-348/432872/20261116152202258_26-348%20NYOAG%20Cert%20Reply.pdf`
   - Confirmed the Solicitor General expressly asked the Court to hold `26-348` pending `26-304` (*Jackson*) as the cleaner lead vehicle, while respondent NYOAG argued to deny both or, in the alternative, grant and consolidate both.
4. `google_web_search(query=""George Kelesis" "District of Nevada" Senate nomination 2026")`
   - Confirmed George Kelesis's February 2026 nomination to serve as U.S. Attorney for the District of Nevada had not been confirmed by the Senate as of November 23, 2026, so no intervening confirmation mootness had arisen.
