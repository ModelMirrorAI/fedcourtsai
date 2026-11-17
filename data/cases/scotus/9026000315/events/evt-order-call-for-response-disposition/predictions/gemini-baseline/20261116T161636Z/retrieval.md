# Retrieval Log

Mode: `forward` (`decided_before: null` in `record/context.json`, `DECIDED_BEFORE` unset). All external lookups were restricted to corpus priors, lower-court and precedent records in CourtListener, and the official Supreme Court docket on `supremecourt.gov`; no third-party forecasts were sought or encountered.

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court scotus --docket 9026000315 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help`
   - Transfer: none (local path resolution and CLI help check).
   - Result: Confirmed `case_id: scotus/9026000315`, `corpus: corpus/corpus.db`, and `outcome: (evaluator-only)`.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 40 GET(s), 10420224 byte(s)`
   - Result: Returned 10 recent `2020s`-era granted SCOTUS cases (cert petitions and substantive interim applications) with distribution counts, CVSG stamps, counsel, and `sal-v8` salience scores.
3. `uv run fedcourts query --court scotus --citation "341 U.S. 267"`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 0 rows, with a CLI note explaining that only 195 SCOTUS rows carry reporter citations and recommending the CourtListener MCP server for known-citation lookups.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from warm cache)
   - Result: Returned 5 recent `2020s`-era denied SCOTUS cert petitions with distribution counts, counsel, and `sal-v8` salience scores.

## 2. Official Supreme Court Docket (`web_fetch`)

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-315.html`
   - Result: Confirmed that as of November 16, 2026, Docket No. 26-315 (*Amy L. Goldman v. Tammy R. Phillips, et al.*) carries the exact same entries as `record/snapshots/2026-11-05.json`, ending with `Nov 04 2026: Response Requested. (Due December 4, 2026)`.

## 3. CourtListener MCP Calls

1. `search` (`type="d"`, `court="ca9"`, `docket_number="24-2249"`)
   - Result: Located the Ninth Circuit docket *Phillips, et al. v. Goldman*, No. 24-2249 (`docket_id=70518255`, filed April 10, 2024).
2. `search` (`type="o"`, `court="ca9"`, `case_name="Phillips v. Goldman"`)
   - Result: Returned 3 cluster entries for *Phillips v. Goldman* (the May 14, 2026 *en banc* opinion, `opinion_id=10855982` / `11323378`, and the November 7, 2025 *en banc* rehearing order, `opinion_id=11199841`).
3. `get_endpoint_schema` (`endpoint_id="docket-entries"`) and `get_endpoint_schema` (`endpoint_id="parties"`)
   - Result: Retrieved REST field schemas for `docket-entries` and `parties`.
4. `search` (`type="o"`, `filed_after="2020-01-01"`, `q='"Mosser v. Darrow" trustee "gross negligence" OR "personal liability"'`)
   - Result: Returned 2 results (both corresponding to the Ninth Circuit *en banc* decision in *Phillips v. Goldman*).
5. `search` (`type="o"`, `q='"United States Trustee" "Mosser v. Darrow" "gross negligence" OR "ordinary negligence"'`)
   - Result: Returned 51 opinion hits; top hit was *In re Big Rivers Electric Corp. (United States v. Schilling)*, 355 F.3d 415 (6th Cir. 2004).
6. `call_endpoint` (`endpoint_id="parties"`, `query={"docket": 70518255, "fields": ["id", "name", "party_types", "extra_info"]}`)
   - Result: Confirmed parties below were Appellants Tammy R. Phillips and Tammy R. Phillips, APLC, Appellee Amy L. Goldman, and Amicus Curiae National Association of Bankruptcy Trustees (confirming the U.S. Trustee did not participate below).
7. `call_endpoint` (`endpoint_id="docket-entries"`, `num_results=100`, `query={"docket": 70518255, ...}`) and `get_more_results` (`query_id="811b96f3"`, `num_results=20`)
   - Result: Retrieved all 101 docket entries in CA9 No. 24-2249, confirming the May 1, 2024 finality show-cause order (`DE 6`), June 11, 2025 three-judge panel oral argument (`DE 67`), August 19, 2025 *sua sponte* *en banc* briefing order (`DE 68`), November 7, 2025 *en banc* grant (`DE 80`), National Association of Bankruptcy Trustees amicus filing (`DE 87, 99, 100`), and January 13, 2026 *en banc* argument (`DE 101`).
8. `read_document` (`opinion_id=11199841`)
   - Result: Verified full text of the November 7, 2025 *en banc* grant order (`1,078` chars, matching `App. 53a`).
9. `search_document` (`opinion_id=[1037770, 2798228]`, `query="Mosser"`), `search` (`type="o"`, `citation="355 F.3d 415"`), and `search_document` (`opinion_id=784780`, `query="Mosser"`)
   - Result: 0 matches in the first two IDs; 60 matches in *In re Big Rivers Electric Corp.*, 355 F.3d 415 (6th Cir. 2004) (`opinion_id=784780`), discussing fiduciary loyalty and fee disgorgement under *Mosser v. Darrow*.
10. `search` (`type="o"`, `court="scotus"`, `q='"Phoenician Mediterranean" OR "Mailman Steam" OR "Dodson" "Smyth" OR "Yadkin Valley Bank"'`) and refined `search` (`type="o"`, `court="scotus"`, `q='"Phoenician Mediterranean" OR "Mailman Steam" OR "Yadkin Valley Bank" OR "DiStefano v. Stern"'`)
    - Result: First query returned 555 broad surname matches (`Dodson`/`Smyth`); refined query returned 0 SCOTUS results, confirming none of those circuit-split decisions drew Supreme Court review.
11. `read_document` (`opinion_id=104898`, `chunk_index=0` and `chunk_index=1`, `chunk_size=12000`)
    - Result: Read full text (`17,805` chars) of *Mosser v. Darrow*, 341 U.S. 267 (1951) (Justice Jackson's majority opinion and Justice Black's dissent).
12. `search` (`type="o"`, `citation="872 F.3d 138"`), `search_document` (`opinion_id=4207197`, `query="gross negligence"`), `read_document` (`opinion_id=9878632`, `chunk_index=[0, 1, 2, 3]`), and `read_document` (`opinion_id=9878633`, `chunk_index=0`)
    - Result: Read *Phoenician Mediterranean Villa, LLC v. Swope (In re J & S Properties, LLC)*, 872 F.3d 138 (3d Cir. 2017), confirming the Third Circuit applied *Harlow* qualified immunity to third-party claims against a Chapter 7 trustee while citing the DOJ *Handbook for Chapter 7 Trustees* (with Judge Fisher concurring in the judgment on quasi-judicial immunity grounds).
13. `search` (`type="o"`, `citation="207 F.3d 758"`), `search` (`type="o"`, `citation="196 F.3d 1"`), and `search` (`type="o"`, `filed_after="2001-01-01"`, `q='"Smyth" "207 F.3d 758" "Mailman Steam"'`)
    - Result: Verified publication dates and citation counts for *Dodson v. Huff (In re Smyth)*, 207 F.3d 758 (5th Cir. 2000), *LeBlanc v. Salem (In re Mailman Steam Carpet Cleaning Corp.)*, 196 F.3d 1 (1st Cir. 1999), and *In re Schooler*, 725 F.3d 498 (5th Cir. 2013).
