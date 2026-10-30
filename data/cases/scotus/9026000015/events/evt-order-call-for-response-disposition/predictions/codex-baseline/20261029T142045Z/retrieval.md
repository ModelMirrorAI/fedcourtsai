# Retrieval record

## Corpus and local context

- `uv run fedcourts paths --court scotus --docket 9026000015 --event evt-order-call-for-response-disposition --role predictor` initially failed because the default uv cache was read-only. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; succeeded and resolved the event path. No outcome was read.
- `uv run fedcourts query --help` initially failed for the same cache reason. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; succeeded. A further help read with `COLUMNS=180` exposed the era and date-filter documentation. These were CLI help requests, not corpus lookups.
- Read `metrics/statpack.md` and the relevant structure and Term/segment values of `metrics/statpack.json`. Computed the prior-Term `sal-v4` baseline reached anchor with jq: 660 / 12,913 = 0.0511112832. Other consulted local files were the instructions, output schemas, and path/serialization helper source; no other cell outputs or topic-label artifacts were opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4`
  - `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
  - Returned four prior docket-Term grant records: U.S. DOGE Service v. U.S. District Court, Corey Duran Berry v. United States, Todd Blanche v. Izuchukwu Ozurumba, and Missionaries of Saint John the Baptist v. Frederic. Their grant dates were October 1 or October 13, 2026; the bare-year filter screens docket/derived year rather than enforcing the provisioned July day boundary. This is a forward cell, so these are not replay leakage, but I did not use these nonanalogous cases as evidence of the target petition's likelihood. No target disposition or subsequent history was requested or returned.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '573 U.S. 682' --decided-before 2026-07-31 --limit 2`
  - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
  - Returned no rows. The CLI reported the July 31 day cutoff and warned that only 200 scoped rows have reporter citations and that the filter matches cases' own citations, not a citation graph. Did not retry sparse filters or interpret absence as a substantive finding.

The transfer lines describe ranged index reads, not an estimated total for all tools. Neither lookup requested full opinion bodies. These are historical-context retrievals from the cell service, not a corpus freshness audit.

## CourtListener MCP

- `search(type="o", citation="485 U.S. 439", num_results=1)` sought Lyng as general precedent, not the target petition. Returned HTTP 429: daily rate limit exceeded, with a reported wait of 1,087 seconds. No opinion text was received. No direct REST fallback or credential access was attempted.

## Web

- One `web.run` search call contained two queries: `site.loc.gov "Lyng" "485 U.S. 439"` and `site.supremecourt.gov "Thomas" "arbiters of scriptural interpretation" "Hobby"`. The tool returned no usable result payload; no search-result claim informed the forecast.
- One `web.run` open call requested the Library of Congress PDF for Lyng, at the path ending `usrep485/usrep485439/usrep485439.pdf`. The tool returned no usable content. No opinion text was received or relied on.

No search sought this petition's disposition, subsequent history, or decision coverage. No live target docket was opened.
