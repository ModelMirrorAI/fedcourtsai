I consulted the merits and per-Justice sections of `metrics/statpack.md` and their underlying counts in `metrics/statpack.json`, including authorship. I used the grant date to select eligible Terms.

- `uv run fedcourts paths --court scotus --docket 9026000426 --event evt-brief-judgment --role predictor` initially failed because the default uv cache was read-only. It succeeded with `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1` and resolved the case and event paths. The same environment settings were used for the following CLI calls.
- `uv run fedcourts query --help` returned the available filters.
- `uv run fedcourts query --court scotus --citation '525 U.S. 471' --citation '596 U.S. 543' --limit 4` returned no rows, with a note that only 195 in-scope rows carry reporter citations. Transfer report: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
- `uv run fedcourts query --court scotus --docket-number 20-322 --limit 2` returned *Garland v. Aleman Gonzalez*, recording a June 13, 2022 reversal. The row carried no opinion text. Transfer report: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
- CourtListener MCP opinion search for SCOTUS docket 20-322, filed after June 12 and before June 14, 2022, requesting one result. The service returned HTTP 429 and no opinion record.
