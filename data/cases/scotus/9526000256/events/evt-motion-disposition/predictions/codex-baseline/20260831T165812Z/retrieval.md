Beyond the provisioned event, context, snapshot, and committed `metrics/statpack.md`, I consulted the following sources.

Corpus lookups:

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 40`
  - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 100 | jq -c 'select(.application_kind == "substantive") | {docket_number, disposition, response_requested, referred_to_court, amicus_briefs, capital_case, date_filed, date_decided}'`
  - `ranged corpus reads: 22 GET(s), 5767168 byte(s)`
- The same `--limit 100` query, piped to a local `jq` aggregate.
  - `ranged corpus reads: 0 GET(s), 0 byte(s)`

CourtListener MCP lookups:

- RECAP search for docket number `25-12952`; no relevant Eleventh Circuit result appeared.
- RECAP search for `"Cassandra Perkins"`; results were unrelated bankruptcy matters.
- RECAP searches limited to the Eleventh Circuit by docket number and by party-name text; neither identified the target appeal.
- Exact-party RECAP searches in the Eleventh Circuit and Northern District of Georgia; the circuit search was empty, while the district search surfaced possible matters that could not be reliably linked.
- Endpoint-schema lookups for `dockets`, `docket-entries`, and `recap-documents`; these supplied no case facts.

No web search was used, and no retrieved result disclosed this application's disposition.
