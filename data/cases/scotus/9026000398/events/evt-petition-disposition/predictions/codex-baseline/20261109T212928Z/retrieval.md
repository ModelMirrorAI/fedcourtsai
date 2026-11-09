# Retrieval record

No search sought Golden's Supreme Court disposition, subsequent history, or decision coverage. No other prediction or evaluation was read. The companion lookup concerns a different case expressly identified by the petition.

## Local sources and tooling

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; read `metrics/statpack.md` for the paid-segment cuts and prior-Term sal-v8 reached rates. The frozen cert anchor came from the provisioned context.
- Initial `uv run fedcourts paths --court scotus --docket 9026000398 --event evt-petition-disposition --role predictor` failed because the default UV cache was read-only. Retried successfully as `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000398 --event evt-petition-disposition --role predictor`.
- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --help` was invoked twice; the second invocation displayed the remainder of the options. No corpus rows retrieved by help or paths.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 25-459 --limit 1`
   - `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned Salazar v. Paramount Global, `scotus/73278510`: cert granted January 26, 2026, two distributions, merits briefing, no recorded merits disposition, last live poll November 5, 2026. Used only for the related-case hold/GVR pathway. No opinion body requested.
2. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --era 2020s --disposition gvr --decided-before 2026 --limit 3` (output projected through `jq` to caption, IDs, disposition, dates, and distribution count).
   - `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
   - Returned Roybal v. Griffith (25-442), Harrington v. Martin (25-1348), and Burford German Funding v. financialright claims (25-1269), marked GVR with two or three distributions. The 2026 argument is a docket-Term bar, not a calendar-date bar: the displayed grants included October/November 2026. This is permissible in forward mode. These unrelated examples were not used as substantive analogues or to estimate grant probabilities.

## CourtListener MCP

1. `search(type="o", q="caseName:(Yershov Gannett)", court="ca1", num_results=3)` returned Yershov, 820 F.3d 482, opinion ID 3199261.
2. `read_document(opinion_id=3199261)` returned the First Circuit opinion; used for its recipient-capability and identification analysis and factual context.
3. `search(type="o", q="caseName:(Solomon Flipps)", court="ca2", num_results=2)` returned Solomon, 136 F.4th 41, opinion ID 10905600.
4. `search_document(opinion_id=10905600, query="Yershov", snippet_size=800)` returned 20 of 51 matches discussing the competing circuit approaches. Used to cross-check the asserted doctrinal disagreement.
5. `search_document(opinion_id=10905600, query="We adopt", snippet_size=1000)` returned no matches. No additional inference drawn from that literal-search miss.
6. `search_document(opinion_id=3199261, query="foreseeable", snippet_size=750)` returned two matches confirming discussion of the recipient's ability to link device/location information to an identified viewer.

## Web attempts

1. One `web.run` search request with queries `site.ca1.uscourts.gov Yershov Gannett 820 F.3d 482` and `site.ca2.uscourts.gov Solomon Flipps 136 F.4th 41` returned no visible content or usable source references.
2. One `web.run` open request for the First Circuit's `15-1719P-01A.pdf`, as identified by CourtListener, likewise returned no visible content. No web-derived facts entered the forecast; the opinion was read through MCP instead.
