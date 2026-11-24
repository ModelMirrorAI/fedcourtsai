# Retrieval log

- `uv run fedcourts query --help` (read the interface).
- `uv run fedcourts query --court scotus --docket-number 26-426`: returned the D.V.D. row (disposition granted, cert granted 2026-09-29, from CA1, merits brief filed 2026-11-16, not decided). stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: refused as a usage error (`modern` is not an era token); returned no rows and I did not re-issue it.
- Read `metrics/statpack.md`: the salience band tables and the relist-count cut.
- No CourtListener MCP calls and no web searches.
