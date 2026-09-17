# Retrieval log

## Corpus tooling

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   Returned 20 recency-ranked granted rows (several substantive applications
   and government-party grants from OT2025). Used for population shape only.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned 20 recency-ranked denied rows, dominated by emergency
   applications. Used for population shape only.

## CourtListener MCP

3. `search` (type `o`, court `ca10`, q `Rogne "City of Catoosa"`), to read the
   Tenth Circuit order below. Failed: HTTP 429, hourly rate limit exceeded.
4. `search` (type `d`, court `scotus`, q `Rogne "City of Catoosa"`), to check
   the live docket for post-snapshot entries. Failed: HTTP 429, hourly rate
   limit exceeded.

No retries; the cell proceeded on the provisioned inputs and the committed
statpack.

## Web searches

None.
