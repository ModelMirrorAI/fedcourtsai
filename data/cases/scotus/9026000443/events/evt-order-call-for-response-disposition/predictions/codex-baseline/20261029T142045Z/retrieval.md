# Retrieval log

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-10-19.json`, `record/documents/documents.json`, `questions-presented.txt`, the petition body, and relevant portions of `appendix.txt`. No other cell's output or realized outcome was read. Related-petition references were taken only from the provisioned petition, not from later docket retrieval.

## Repository reference material

Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction and feedback schemas, and `metrics/statpack.md`. Used `metrics/statpack.json` to pool the nine strictly-prior rendered baseline-band risk sets: 660 / 12,913 = 0.0511112832. Also inspected path/serialization helpers and model class locations solely to construct and validate the authorized output files.

## Corpus and CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000443 --event evt-order-call-for-response-disposition --role predictor`: failed before retrieval because the default uv cache was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`; it identified the event path and did not read an outcome.
2. `uv run fedcourts query --help`: first attempt failed for the same cache permission reason. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`. Repeated help with `COLUMNS=160`, and then with `NO_COLOR=1 COLUMNS=110`, to inspect the rendered structured filters. These help calls performed no corpus retrieval.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`: succeeded. Exact transfer report: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`. Returned U.S. DOGE Service, No. 25-1103; Corey Duran Berry, No. 25-7026; and Todd Blanche v. Izuchukwu Ozurumba, No. 25-1343. These are illustrative selected grant rows, not a population or ERISA-matched estimate. The Term filter deliberately excludes the target's 2026 docket Term.
4. Repeated the identical filtered query and projected only identifiers, captions, disposition, distribution count, CVSG date, and grant date with `jq` because the first terminal display was truncated. Exact transfer report: `ranged corpus reads: 0 GET(s), 0 byte(s)`. Same three rows; no additional prior population.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`: failed with `ValueError` because the service backend has no client-side connection for that command. Consequently no corpus-wide freshness stamp is claimed. No corpus refresh or direct remote access was attempted.

## General legal-context attempts

All web attempts concerned general Court rules, not this case or the related petitions. Each returned no usable content to this engine, so none supplied evidence for the forecast:

1. Web open of `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
2. Web find of `compelling reasons` in that PDF.
3. Web search: `site.supremecourt.gov Rule 10 considerations governing review certiorari conflict courts appeals`.
4. Web open of `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
5. Repeat web open of the same rules-guidance page.

One CourtListener MCP search: `type=o`, `citation=559 U.S. 506`, `court=scotus`, `num_results=1`, fields `caseName,dateFiled,citation,absolute_url,opinions`. This was an attempted check of Conkright v. Frommert, an older general ERISA authority cited in the petition. It returned HTTP 429, with the daily limit exhausted and an approximately 11,453-second retry interval. No opinion text was obtained and no REST fallback was attempted. The forecast instead relies on the provisioned advocacy and appellate opinion, with those limits stated in `reasoning.md`.
