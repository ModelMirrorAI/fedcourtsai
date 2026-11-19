Consulted the provisioned snapshot, context, event definition, and all three provisioned application filings. Beyond those inputs, consulted the prediction contract and schemas, metrics/statpack.md (the interim section and applicant-class table), and the interim Term rows/applicant_cuts in metrics/statpack.json. Computed the 2016–2025 finer-reading pool locally as 156/1,337 and the private/capital cut as 10/288. No web search, own-case docket retrieval, linked-petition retrieval, or other predictor's forecast was consulted.

CLI and corpus calls, including unsuccessful attempts:

1. `uv run fedcourts paths --court scotus --docket 9526000686 --event evt-brief-response-disposition --role predictor` failed before execution because uv's default cache was read-only. No corpus read occurred.
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 9526000686 --event evt-brief-response-disposition --role predictor` succeeded and identified the case and event paths; it exposed no outcome path.
3. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` returned the supported structured filters.
4. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --citation '523 U.S. 272' --limit 1 --full` returned no rows and a citation-coverage warning: only 195 SCOTUS rows in scope carried reporter citations. The empty result is not evidence that Woodard is absent as precedent. Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. No opinion body was returned.
5. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 4` returned four unrelated resolved certiorari petitions: Mizrahi v. United States (25-1238), Khatibi v. Yip (25-1240), Strickland v. Moritz (25-1303), and Novotny v. Moore (25-1324). They were not used as analogues for this capital application. Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`.

CourtListener MCP calls, in order:

1. `search` with `query='citation:"66 F.4th 896"'`, `type='o'`, and fields `id, caseName, dateFiled, citation, opinions, absolute_url, snippet` was refused: `query` is an unsupported argument. No results were returned.
2. `search` with `q='citation:"66 F.4th 896"'`, `type='o'`, and the same fields returned one result: Darryl Barwick v. Governor of Florida, April 26, 2023, 66 F.4th 896, cluster URL https://www.courtlistener.com/opinion/9394630/darryl-barwick-v-governor-of-florida/ and opinion id 9390106. Query id: a4fdddcb. The response warned that some requested fields were unavailable; the relevant case metadata and opinion id were present.
3. `get_endpoint_schema` with `endpoint_id='opinions'` returned the supported query fields.
4. `call_endpoint` with `endpoint_id='opinions'`, `query={"id":9390106,"fields":["id","plain_text"]}` returned the full 14-page Barwick opinion. Query id: dfe56988. Its treatment of Woodard's minimal clemency safeguards and its refusal to find delay on that record informed the rationale. It is a different prisoner's historical case, not Overton's disposition.

Validation is a local contract check, not retrieval. Commands use the preinstalled environment with caching disabled and synchronization skipped; no packages were installed.
