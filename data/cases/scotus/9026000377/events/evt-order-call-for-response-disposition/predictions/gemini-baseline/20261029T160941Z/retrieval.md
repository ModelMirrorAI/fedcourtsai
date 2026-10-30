# Retrieval Log

## 1. Local CLI & Corpus Queries (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000377" --event "evt-order-call-for-response-disposition" --role predictor`
   - Verified case ID (`scotus/9026000377`), corpus path, and event path.
2. `uv run fedcourts query --court scotus --citation "597 U.S. 450" --citation "527 U.S. 1" --citation "602 U.S. 821" --limit 10`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (note indicated only 200 rows in scope carry reporter citations).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 31 GET(s), 7929856 byte(s)`
   - Returned 10 recent 2020s granted SCOTUS cases (including OT2026 cert grants).
4. `uv run fedcourts query --court scotus --docket-number 25-7026`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Returned 1 row (`scotus/73283862`, *Corey Duran Berry v. United States*, granted October 13, 2026).
5. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent 2020s GVR dispositions on SCOTUS dockets.
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 5 recent 2020s denied SCOTUS dispositions.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", q=""Ruan v. United States" "Neder" harmless error")`
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 4918 seconds.'}`. Degraded gracefully to provisioned inputs and corpus tooling per prompt instructions.

## 3. Web Fetches & Web Searches (Forward Mode)

1. `web_fetch` on `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-377.html` and `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-7026.html`
   - Result: Confirmed Docket No. 26-377 (*Frank Parasmo v. United States*) remains pending at the October 5, 2026 "Response Requested. (Due November 4, 2026)" stage with no newer entries. Retrieved docket entries for No. 25-7026 (*Berry v. United States*).
2. `web_fetch` on `https://www.supremecourt.gov/docket/qp/25-07026qp.pdf`
   - Result: Failed with HTTP 404 Not Found.
3. `google_web_search` for `"Corey Duran Berry" OR "25-7026" "United States" Supreme Court`
   - Result: Confirmed *Berry v. United States* (No. 25-7026) concerns the standard for a Certificate of Appealability under 28 U.S.C. § 2253(c), unrelated to *Ruan* or *Neder* harmless-error review.
