All corpus commands used the provisioned virtual environment with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache` and `UV_NO_SYNC=1` on the successful calls.

- `uv run fedcourts paths --court scotus --docket 9026000110 --event evt-order-call-for-response-disposition --role predictor` initially failed to initialize the default read-only uv cache. Retrying with the temporary cache returned the case, corpus and event paths.
- `uv run fedcourts query --help` returned the structured filters and docket-number lookup syntax.
- Read the committed `metrics/statpack.md` modern-cert, relist, CVSG, amicus, per-Term and salience-band tables.
- `uv run fedcourts query --court scotus --docket-number 20-1212 --limit 1` returned *Pakdel v. City and County of San Francisco*, with a June 28, 2021 grant date, a disposition recorded as `gvr`, and no stored opinion body. Transfer reported `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
- CourtListener MCP opinion search for *Walls*, Fourth Circuit No. 25-1121, filed between February 22 and 24, 2026, returned zero results. I used the provisioned related docket for its procedural history.
- CourtListener MCP opinion search for *74 Pinehurst*, Supreme Court orders with related opinions filed in February 2024, returned the February 20 statement, opinion ID 9942065.
- `uv run fedcourts query --court scotus --docket-number 22-1130 --limit 1` returned *74 Pinehurst LLC v. New York*, denied February 20, 2024, with 13 distributions. Transfer reported `ranged corpus reads: 1 GET(s), 262144 byte(s)`.
- CourtListener MCP `read_document`, opinion ID 9942065, chunk 0 of size 4,600, returned Justice Thomas’s statement respecting the denials in *74 Pinehurst* and *335–7 LLC*. He identified specific pleading problems in those challenges to New York’s eviction restrictions.
