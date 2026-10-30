# Retrieval Log

## Corpus CLI Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000187" --event "evt-order-call-for-response-disposition" --role predictor`
   - Resolved `case_id: scotus/9026000187`, `corpus: corpus/corpus.db`, `event: data/cases/scotus/9026000187/events/evt-order-call-for-response-disposition/event.yaml`.
2. `uv run fedcourts query --help`
   - Inspected structured filter options.
3. `uv run fedcourts query --court scotus --docket-number "26-187" --limit 5`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned 1 row (`scotus/9026000187`, `26-187`, originating court `ca5`, docket `25-10886`, `distribution_count: 1`, `salience_score: 0.0337`, `salience_version: sal-v4`).
4. `uv run fedcourts query --court scotus --citation "576 U.S. 389" --limit 10`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 28 GET(s), 7143424 byte(s)`
   - Returned 10 recent granted SCOTUS priors from the 2020s era.
6. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 5 recent denied SCOTUS rows from the 2020s era (served from warm cache).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Congious v. Shaw", fields=["caseName", "docketNumber", "court_id", "dateFiled", "citation", "docket_id", "cluster_id"])`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 1948 seconds.`).
2. `mcp_courtlistener_search(type="o", q=""Short v. Hartman" "Kingsley"", fields=["caseName", "docketNumber", "court_id", "dateFiled", "citation"])`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 1948 seconds.`).

## Web Searches

- None attempted.
