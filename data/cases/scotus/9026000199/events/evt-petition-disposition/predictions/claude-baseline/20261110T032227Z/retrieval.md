# Retrieval log

Corpus (`uv run fedcourts query`):
1. `uv run fedcourts query --help`: usage text.
2. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage
   error (`modern` is not an era value). Re-issued as #5.
3. `uv run fedcourts query --court scotus --docket-number 26-201`: `ranged corpus reads: 18 GET(s),
   4718592 byte(s)`. Returned the FTC companion row.
4. `uv run fedcourts query --court scotus --docket-number 25-1325` (run plain, then with
   `--include-open`): `ranged corpus reads: 1 GET(s), 262144 byte(s)`. *Oklahoma v. United
   States* (CA6): distributed 2026-10-09, distribution_count 1, no disposition.
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3`:
   `ranged corpus reads: 23 GET(s), 6029312 byte(s)`. A generic sample of granted rows, not
   relevant.

Committed files: `metrics/statpack.md`, the "Segment base rate by salience band (sal-v8)" table.

No CourtListener MCP calls and no web searches.
