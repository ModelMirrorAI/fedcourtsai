# Retrieval
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` returned usage text only (`--era` with that value was not accepted). No rows.
- `uv run fedcourts query --docket-number 23-9` returned usage text only. No rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  printed `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. It returned generic recent grants with nothing case-specific.
- `uv run fedcourts query --help` (usage read).
- Read the committed `metrics/statpack.md` (CVSG and amicus cuts).
- No CourtListener MCP calls and no web searches.
