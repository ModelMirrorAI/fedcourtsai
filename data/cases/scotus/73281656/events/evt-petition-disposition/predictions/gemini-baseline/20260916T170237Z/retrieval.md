# Retrieval Log

1. `fedcourts query scotus --era 2020s --text "cumulative error" "ineffective assistance"` (Failed with error)
2. `fedcourts query --court scotus --disposition granted --limit 1`
   - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
3. Courtlistener MCP Search: `search` tool with `docket_number=25-1176, type=d` (Results: no matching scotus docket found)
4. Read `metrics/statpack.md` for baseline band grant rates and capital case grant rates.
