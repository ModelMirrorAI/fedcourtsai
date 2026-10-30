# Retrieval Log

## Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000562" --event "evt-petition-arrival-disposition" --role predictor`
   - Resolved `case_id` (`scotus/9026000562`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts query --help`
   - Inspected available structured filters for corpus prior retrieval.
3. `uv run fedcourts query --court "scotus" --limit 10`
   - `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Returned 10 recent resolved SCOTUS rows from October 2026 (`scotus/9026000002`, `scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9026000346`, `scotus/9026005347`, `scotus/9526000512`, `scotus/9526000555`, `scotus/9526000556`, `scotus/9526000416`).
4. `uv run fedcourts query --court "scotus" --docket-number "26-562"`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned the open corpus row for `scotus/9026000562` (`26-562`, `disposition: null`, `distribution_count: 0`, `last_live_polled: "2026-10-30"`), confirming the petition remains undecided and pending at arrival.

## CourtListener MCP & Web Search

- None attempted beyond the provisioned inputs and `fedcourts` corpus queries.
