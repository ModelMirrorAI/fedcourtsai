# Retrieval log

- `uv run fedcourts query --help` (usage text).
- `uv run fedcourts query --court scotus --disposition affirmed --era modern` — refused: `affirmed` is not a disposition label on this surface. No rows.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — returned 5 recent granted rows, none related to this case; not used in the forecast. stderr: `ranged corpus reads: 33 GET(s), 8585216 byte(s)`.
- `metrics/statpack.md`, merits-docket and per-Justice sections (committed file).
- No CourtListener MCP calls and no web searches.
