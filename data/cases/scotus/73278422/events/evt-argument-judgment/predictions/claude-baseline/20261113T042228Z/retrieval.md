# Retrieval log

- `uv run fedcourts query --help` — read the flags.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (printed help); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 33 GET(s), 8585216 byte(s)`; five recent granted rows, none bearing on this case.
- `metrics/statpack.md` — merits docket section and per-Justice votes section.
- No CourtListener MCP calls and no web searches.
