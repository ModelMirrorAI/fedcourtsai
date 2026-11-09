# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (`modern` is not an era value). The help text came back and no rows were returned; no `ranged corpus reads` line was printed.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5`: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`. It returned five recent GVRs (e.g. 25-442, 25-1348, 26-5123), used only as context for the GVR route.
- Read `metrics/statpack.md` (relist-count and CVSG-status paid-segment cuts).
- No CourtListener MCP or web searches.
