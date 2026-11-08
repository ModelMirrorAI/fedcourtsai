# Retrieval
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 3`: rejected with a usage error, because `modern` is not a decade token.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 3`, which printed `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. It returned generic 2020s denied rows (Guardado v. Florida and others) that are not on point. Used for context only.
- Read the committed `metrics/statpack.md` (the relist-count cut for the paid scored segment).
- No CourtListener MCP calls and no web searches.
