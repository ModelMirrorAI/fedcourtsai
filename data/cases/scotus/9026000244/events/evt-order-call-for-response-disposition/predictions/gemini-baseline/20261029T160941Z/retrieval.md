# Retrieval Log

## 1. Corpus Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000244" --event "evt-order-call-for-response-disposition" --role predictor`
   - Transfer line: none (`paths` command).
   - Result: Resolved `case_id` (`scotus/9026000244`), `corpus` (`corpus/corpus.db`), and `event` path.

2. `uv run fedcourts query --help`
   - Transfer line: none.
   - Result: Inspected structured filter options for `fedcourts query`.

3. `uv run fedcourts query --court scotus --docket-number 26-244`
   - Transfer line: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned the corpus row for `scotus/9026000244` (*The Kroger Co., dba Fred Meyer, Inc. v. Elisha Solano, Individually and on Behalf of Other Customers, et al.*), confirming `disposition: null`, `distribution_count: 1`, `salience_score: 0.0248`, and the two amicus counsel entries (`The Retail Litigation Center, Inc.` and `Chamber of Commerce of the United States of America, American Tort Reform Association, and Business Roundtable`).

4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 31 GET(s), 7929856 byte(s)`
   - Result: Returned 10 recent granted SCOTUS cases from the 2020s era (OT2026 grants including `26-12`, `26-204`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, `26-104`).

5. `uv run fedcourts query --court scotus --citation "605 U.S. 327" --citation "594 U.S. 413" --citation "577 U.S. 442" --limit 10`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 0 rows with note explaining that the `citations` column is sparsely populated (200 SCOTUS rows in scope).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(case_name="Solano v. Kroger", type="o")`
   - Result: Failed with HTTP 429 rate-limit error (`Request was throttled. Rate limit exceeded: 1400/day. Expected available in 8437 seconds.`).

2. `mcp_courtlistener_search(q=""uninjured class members" "23(b)(3)"", type="o")`
   - Result: Failed with HTTP 429 rate-limit error (`Request was throttled. Rate limit exceeded: 1400/day. Expected available in 8437 seconds.`).

## 3. Web Searches and Fetches (Forward Mode)

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-244.html` (twice)
   - Result: Returned the four proceedings entries up to Sep 03, 2026 (`Aug 17 2026` Petition filed; `Aug 31 2026` Waiver filed; `Sep 02 2026` Distributed for Conference of 9/28/2026; `Sep 03 2026` Response Requested, due October 5, 2026).

2. `google_web_search(query=""26-244" "Kroger" "Solano" supreme court")`
   - Result: Confirmed that Docket No. 26-244 is still pending before the Supreme Court as of late October 2026, that amicus briefs were filed on October 5, 2026 in support of petitioner by the U.S. Chamber of Commerce, the Retail Litigation Center, and the American Tort Reform Association, and that respondents' brief in opposition deadline was extended to November 4, 2026.

3. `google_web_search(query=""uninjured class members" "Rule 23" certiorari 2025 2026 "Laboratory Corp"")`
   - Result: Summarized the June 5, 2025 8-1 dismissal as improvidently granted in *Laboratory Corp. of America Holdings v. Davis*, 605 U.S. 327 (2025), Justice Kavanaugh's solo dissent, and competing 2026 certiorari petitions raising the same Rule 23(b)(3) uninjured-class-member question (*Drake v. Bayer Healthcare LLC*, *Nestlé USA, Inc. v. Falcone*, and *The Kroger Co. v. Solano*).

4. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/docket_js/26-244.json` and `https://www.supremecourt.gov/RSS/cases/26-244.xml`
   - Result: Empty response (endpoints not publicly served at those paths).

5. `web_fetch` on `https://www.scotusgate.com/dockets/26-244`
   - Result: Unable to access URL due to site restrictions.
