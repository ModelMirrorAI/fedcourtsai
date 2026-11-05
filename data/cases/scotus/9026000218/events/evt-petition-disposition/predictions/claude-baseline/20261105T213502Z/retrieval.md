# Retrieval log

- `uv run fedcourts query --docket-number 20-7311` → usage error (needs `--court`). No corpus read.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` → usage error (unknown era 'modern'). No corpus read.
- `uv run fedcourts query --court scotus --docket-number 20-7311` (the petitioner's 2021 petition)
  - stderr: `ranged corpus reads: 695 GET(s), 181993472 byte(s)`
  - Returned a sparse row (originating court `la`, filed 2021-03-03, disposition null). The petition itself reports that it was denied on May 3, 2021.
- `uv run fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 8`
  - stderr: `ranged corpus reads: 949 GET(s), 248578048 byte(s)`
  - Returned no rows.
- Base rates came from the committed `metrics/statpack.md`: the modern cert, relist, CVSG, amicus and salience-band cuts, and the sal-v7 per-Term band table.
- No CourtListener MCP calls and no web searches.
