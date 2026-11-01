# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 5` returned a usage error (the `--era` value was rejected or unusable). I re-issued the query without it.
- `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 5` returned `ranged corpus reads: 6 GET(s), 1572864 byte(s)`. It gave five recent OT2026 denied applications, including pro se substantive stays such as 26A535. These were used for the population's shape only.
- I read `metrics/statpack.md`, section "The interim docket (applications)", for the base rate.
- No CourtListener MCP calls and no web searches.
