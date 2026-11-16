# Retrieval Log — `scotus/9026000315` (`evt-petition-disposition`)

## 1. `fedcourts` CLI & Corpus Queries

1. `uv run fedcourts paths --court "scotus" --docket "9026000315" --event "evt-petition-disposition" --role predictor`
   - Transfer line: *(none — path resolution command)*
   - Result: Resolved `case_id` (`scotus/9026000315`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts query --help`
   - Transfer line: *(none — CLI help)*
   - Result: Displayed structured query flags.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 40 GET(s), 10420224 byte(s)`
   - Result: Returned 10 recent granted SCOTUS priors in the 2020s era (including OT2026 grants with distribution counts, salience scores, and CVSG markers).
4. `uv run fedcourts query --court scotus --citation "341 U.S. 267" --limit 5`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 0 rows with coverage note (`citations` column populated on 195 SCOTUS rows).
5. `uv run fedcourts query --court scotus --docket-number 26-315`
   - Transfer line: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: Returned the corpus metadata row for `scotus/9026000315` (`salience_score: 0.0248`, `distribution_count: 1`, `last_live_polled: 2026-11-16`).
6. `uv run fedcourts query --court scotus --docket-number 26A137`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned the corpus row for linked extension application `26A137` (`scotus/9526000137`, filed by Roy T. Englert Jr. on 2026-07-28, granted 2026-07-29).
7. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Result: Returned 10 recent denied SCOTUS cert priors from the November 13, 2026 conference (`date_decided: 2026-11-16`), showing distribution counts and salience context for denied paid petitions.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", citation="176 F.4th 1152", num_results=5)`
   - Result: `count: 0` (reporter citation not yet indexed on the cluster).
2. `mcp_courtlistener_search(type="o", q=""Mosser v. Darrow" "willful and deliberate" trustee personal liability", filed_after="2013-01-01", num_results=15)`
   - Result: `count: 4` — returned *Randall Goulding v. Leslie Weiss* (`ca7`, cluster `4645957`/`4645917`), *Phoenician Mediterranean Villa, LLC v. Swope (In Re J & S Properties, LLC)* (`ca3`, cluster `4429944`), and two bankruptcy court opinions.
3. `mcp_courtlistener_search(type="o", court="ca9", docket_number="24-2249", num_results=10)`
   - Result: `count: 2` — returned *Phillips v. Goldman* (`2026-05-07` en banc opinion, cluster `10855982`; and `2025-11-07` sua sponte en banc order, cluster `10733256`).
4. `mcp_courtlistener_search(type="o", q=""Mosser v. Darrow" trustee "personal liability" OR "personally liable"", filed_after="2010-01-01", num_results=15)`
   - Result: `count: 26` — returned circuit and bankruptcy decisions applying *Mosser v. Darrow*, including *In re Schooler* (`ca5`, `12-10677`) and *In re McKenzie* (`ca6`).
5. `mcp_courtlistener_search(type="o", court="scotus", q=""Mosser v. Darrow" OR ("Chapter 7 trustee" AND immunity)", num_results=15)`
   - Result: `count: 9` — returned *Mosser v. Darrow* (`341 U.S. 267` and cert grant `340 U.S. 928`) and subsequent Supreme Court opinions citing *Mosser* (e.g., *Wolf v. Weinstein*, `372 U.S. 633`).
6. Parallel batch of 5 calls hitting temporary HTTP 429 rate limit (`Rate limit exceeded: 25/min`):
   - `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10855982)` -> HTTP 429 error.
   - `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=4429944)` -> HTTP 429 error.
   - `mcp_courtlistener_search_document(opinion_id=[4429944, 4645917], query="Mosser")` -> HTTP 429 error on both IDs.
   - `mcp_courtlistener_search(type="o", court="scotus", q=""Mailman Steam" OR "Lehal Realty" OR "Liberty Mutual" Schooler OR "Phoenician Mediterranean" OR "Goulding" Weiss OR "Konvalinka" McKenzie")` -> HTTP 429 error.
   - `mcp_courtlistener_search(type="d", court="ca9", docket_number="24-2249")` -> HTTP 429 error.
7. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10855982)` (retry)
   - Result: Returned cluster `10855982` (*Phillips v. Goldman*, `2026-05-07`) with single `sub_opinions` entry (`11323378`), confirming no separate concurring or dissenting opinion files.
8. `mcp_courtlistener_search_document(opinion_id=[4429944, 4645917], query="Mosser", snippet_size=400)` (retry)
   - Result: `0` matches because `4429944` and `4645917` were cluster IDs rather than opinion IDs (matched unrelated older opinion IDs).
9. `mcp_courtlistener_search(type="o", court="scotus", q=""Mailman Steam" OR "Lehal Realty" OR "Liberty Mutual" Schooler OR "Phoenician Mediterranean" OR "Goulding" Weiss OR "Konvalinka" McKenzie", num_results=20)` (retry)
   - Result: `count: 268` (broad match on `McKenzie` / `Weiss` / `Schooler` surnames in unrelated SCOTUS order lists).
10. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=4429944)` (retry)
    - Result: Returned Third Circuit cluster `4429944` (*Phoenician Mediterranean Villa, LLC v. Swope (In Re J & S Properties, LLC)*, `2017-09-28`, Judges Hardiman, Roth, Fisher; opinion IDs `9878632`, `9878633`, `4207197`).
11. `mcp_courtlistener_search(type="o", court="scotus", q=""Mailman Steam" OR "Lehal Realty" OR "Schooler" "Liberty Mutual" OR "Swope" "Phoenician"", num_results=10)`
    - Result: `count: 0`.
12. `mcp_courtlistener_search_document(opinion_id=9878632, query="negligen", snippet_size=350)`
    - Result: `match_count: 0` across `38,013` chars, confirming the Third Circuit's *J & S Properties* decision addressed constitutional qualified immunity rather than common-law negligence liability.

## 3. Web Fetches (`forward` mode — official Supreme Court docket & filing only)

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-315.html` and `https://www.supremecourt.gov/DocketPDF/26/26-315/425581/20260924152750533_26-315%20Amicus%20Brief.pdf`
   - Result: Confirmed the live official docket entries match snapshot `2026-11-16.json` exactly through `Nov 04 2026: Response Requested. (Due December 4, 2026)` with no later filings or orders, and extracted the arguments and signatories of the September 24, 2026 amicus brief of retired bankruptcy judges Hon. Leif Clark, Hon. Melanie Cyganowski, Hon. Bruce Markell, Hon. Eugene Wedoff, and Prof. Nancy Rapoport (focusing on Chapter 7 panel trustee fee structure, insurance/bonding costs, and defensive litigation incentives under a simple-negligence rule).
