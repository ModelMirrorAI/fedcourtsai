# Retrieval log

- `uv run fedcourts query --help` — read the interface.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 8` — rejected: `modern` is not an era token (usage error, no rows).
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 6` — returned 6 granted SCOTUS priors (mostly federal-petitioner and high-profile cases; none on government contracts). stderr: `ranged corpus reads: 34 GET(s), 8847360 byte(s)`.
- `metrics/statpack.md` — relist-count, CVSG-status and amicus-count cuts (paid scored segment), originating-court row for `cafc`, and the sal-v8 salience band table.
- No CourtListener MCP calls and no web searches.
