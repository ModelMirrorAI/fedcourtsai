# Retrieval log

- `uv run fedcourts query --help` — read the interface.
- `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications` — refused: unknown era `modern` (usage text returned).
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --include-applications --limit 8` — 8 recent denied rows (pro se and capital applications, extensions). stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`.
- Read the committed `metrics/statpack.md` interim section and looked up the `finer_resolved` keys in `metrics/statpack.json`.
- No CourtListener MCP calls and no web searches.
