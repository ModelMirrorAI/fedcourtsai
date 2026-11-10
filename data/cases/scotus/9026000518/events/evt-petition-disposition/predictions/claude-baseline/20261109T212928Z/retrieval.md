# Retrieval log
- Read `metrics/statpack.md`: the modern-cert, circuit, relist, CVSG and amicus cuts, and the sal-v8 band table.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error, "Unknown era 'modern'". No rows returned.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`. Stderr printed `ranged corpus reads: 32 GET(s), 8388608 byte(s)`. It returned recent granted priors, none of them on point; used only as context.
- WebFetch https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-518.html. The live docket matches the snapshot, and there are no entries after Oct 27, 2026.
- No CourtListener MCP calls.
