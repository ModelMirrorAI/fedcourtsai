# Retrieval

- `uv run fedcourts query --help`: read the interface.
- `uv run fedcourts query --court scotus --docket-number 24-421`: stderr `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned the State's earlier petition in this case (Davis v. Smith, CA6 23-3604), denied 2025-01-27 after 3 distributions.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: refused (unknown era token). Re-issued with the `2020s` token below.
- `uv run fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 8`: stderr `ranged corpus reads: 899 GET(s), 235274240 byte(s)`. No rows returned.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 8`: stderr `ranged corpus reads: 3 GET(s), 786432 byte(s)`. Eight recent GVRs, none on point.
- Base rates: `metrics/statpack.md` (sal-v4 segment table, relist/CVSG cuts, CA6 circuit cut).
- No CourtListener MCP calls and no web searches.
