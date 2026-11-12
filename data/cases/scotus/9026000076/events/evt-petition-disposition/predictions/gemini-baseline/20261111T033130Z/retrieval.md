# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. Command:
   ```bash
   uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5
   ```
   Stderr:
   ```text
   ranged corpus reads: 32 GET(s), 8388608 byte(s)
   ```
   Summary of results: Returned 5 recent granted SCOTUS rows from the 2020s era (26A560, 25-1408, 26A512, 26-12, 26-204) for general recent-docket context.

## CourtListener MCP Lookups

None.

## Web Searches

None.
