# Retrieval Log

## Corpus CLI (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26A715`
   - Stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned 1 row (`scotus/9526000715`, *Rachel Beth Odom v. Oklahoma*, `26A715`), confirming the linked substantive stay application originated from the Court of Civil Appeals of Oklahoma, Third Division (`123,076`), and was denied on `2026-11-19` with `response_requested: false`, `referred_to_court: false`, and `amicus_briefs: 0`.

2. `uv run fedcourts query --court scotus --docket-number 26M23`
   - Stderr: `ranged corpus reads: 746 GET(s), 195559424 byte(s)`
   - Stderr note: `note: docket-number lookup: no row for 26M23 (scotus) — the corpus holds no such number in scope, or the other filters screened it; the CourtListener MCP server can look a docket up by number`
   - Result: 0 rows returned (`M`-docket sealing motions are outside corpus scope).

3. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   - Stderr: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Result: Returned 5 recent 2020s SCOTUS rows for general docket/application context.

4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 5 recently granted OT2025/OT2026 SCOTUS petitions and applications (`25-944`, `26-239`, `26A560`, `25-1408`, `26A512`), illustrating typical counsel, amicus, and distribution profiles of granted matters.

*(Note: `uv run fedcourts paths --court "scotus" --docket "9026000502" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help` were also run locally with no corpus reads.)*

## CourtListener MCP

1. `mcp_courtlistener_search(type="o", q='"Baxter v. Palmigiano" "Lefkowitz" parental OR deprivation OR custody')`
   - Result: `count: 256` (`query_id: 4cb8c8a9`). Surfaced *Baxter v. Palmigiano*, 425 U.S. 308 (1976), *Lefkowitz v. Cunningham*, 431 U.S. 801 (1977), and state appellate decisions applying *Baxter* in child-dependency proceedings, including *In re Dependency of A.M.F.*, 526 P.3d 32 (Wash. 2023) (`opinion_id: 11264705`).

2. `mcp_courtlistener_search(type="o", case_name="Odom", q='"Rachel" "Odom" Oklahoma')`
   - Result: `count: 0` (`query_id: 1f506c5f`). Confirmed the unpublished Oklahoma Court of Civil Appeals decision in juvenile/deprivation Case No. 123,076 is not published on CourtListener.

3. `mcp_courtlistener_search_document(opinion_id=11264705, query="Baxter", snippet_size=400)`
   - Result: `match_count: 23`, 20 snippets returned from *In re Dependency of A.M.F.*, 526 P.3d 32 (Wash. 2023), showing how state supreme courts reconcile *Baxter*, *Spevack*, *Garrity*, and *Lefkowitz* in child-dependency adjudications (forbidding meeting the State's burden *solely* through silence while permitting adverse inferences alongside probative evidence).

## Web Fetch (Forward Mode — Official Supreme Court Docket)

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-502.html`
   - Result: Confirmed the official public docket entries for No. 26-502 (linked with `26M23`, decision date March 9, 2026, discretionary court decision date June 1, 2026, August 28 sealing motion and petition filing, September 16 distribution for 10/9/2026 conference, October 13 motion granted, October 15 docketing) and verified no disposition or post-snapshot Call for a Response had been entered.
