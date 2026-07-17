# Retrieval

## Base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-circuit, relist-count, CVSG-status, and per-Term tables.
- Consulted the 2025 Term paid-filing detail in `metrics/statpack.json`.

## Corpus lookup

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '601 U.S. 416' --limit 8 --corpus-backend ranged`
- Result: failed because the configured corpus host could not be resolved. The command failed before completing a ranged read and emitted no `ranged corpus reads: ...` line.

No CourtListener MCP lookup or web search was used. No information about this case's disposition was sought or encountered.
