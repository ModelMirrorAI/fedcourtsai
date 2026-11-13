# Retrieval log

- `uv run fedcourts query --help` — read the flags.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (flag value not accepted); nothing returned.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — returned 5 recent granted SCOTUS rows, none related to this case; not used. stderr: `ranged corpus reads: 33 GET(s), 8585216 byte(s)`.
- Read the committed `metrics/statpack.md` (merits docket section and per-Justice merits votes section).
- No CourtListener MCP calls and no web searches.
