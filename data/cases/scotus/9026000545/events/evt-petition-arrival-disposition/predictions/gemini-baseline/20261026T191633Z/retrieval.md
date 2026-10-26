# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`

*(Note: An initial attempt `uv run fedcourts query --court scotus --text "similarly situated in all material respects Title VII comparator Lewis" --limit 10` exited with usage error code 2 before any corpus read because `--text` is not a supported flag.)*

## CourtListener MCP Lookups

- None.

## Web Searches

- None.
