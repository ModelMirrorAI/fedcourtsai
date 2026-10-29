# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS granted cases (used to inspect corpus schema and recent OT2025/OT2026 grants).

2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS denied cases from warm cache.

3. `uv run fedcourts query --court scotus --docket-number 25-6344`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned `scotus/73282036` (*Ralph Kevin Tovar v. United States*, No. 25-6344), originating from the Eleventh Circuit (`23-10755`), showing `disposition: "denied"` and `date_cert_denied: "2026-05-18"` after `distribution_count: 2`.

4. Attempted `uv run fedcourts query` calls rejected for unsupported CLI flags:
   - `uv run fedcourts query --court scotus --attorney "David A. O'Neil" --limit 10` — failed with `Error: No such option: --attorney`.
   - `uv run fedcourts query --court scotus --originating-court ca3 --era 2020s --disposition granted --limit 10` — failed with `Error: No such option: --originating-court`.
   - `uv run fedcourts query --court scotus --originating-court ca3 --era 2020s --disposition denied --limit 10` — failed with `Error: No such option: --originating-court`.

## CourtListener MCP Lookups

None.

## Web Searches

None.
