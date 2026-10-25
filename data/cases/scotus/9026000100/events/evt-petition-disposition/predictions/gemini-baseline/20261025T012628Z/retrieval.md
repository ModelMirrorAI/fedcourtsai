# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. Command:
   ```bash
   uv run fedcourts query --court scotus --era 2020s --limit 10
   ```
   Stderr transfer line:
   `ranged corpus reads: 6 GET(s), 1572864 byte(s)`

2. Command (invalid flag check, no corpus transfer):
   ```bash
   uv run fedcourts query --court scotus --attorney "Robert Mark Loeb" --limit 20
   uv run fedcourts query --court scotus --attorney "Kelly J. Shackelford" --limit 20
   ```
   Stderr transfer line: none (CLI usage error; `--attorney` is not a supported flag).

3. Command (lookup of prior *Hittle v. City of Stockton*, No. 24-427):
   ```bash
   uv run fedcourts query --court scotus --docket-number "24-427"
   ```
   Stderr transfer line:
   `ranged corpus reads: 6 GET(s), 1441792 byte(s)`

## CourtListener MCP Lookups
None.

## Web Searches
None.
