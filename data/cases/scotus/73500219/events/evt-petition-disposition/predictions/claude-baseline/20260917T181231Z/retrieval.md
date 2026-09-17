# Retrieval log (claude-baseline, run 20260917T181231Z)

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   Returned recency-ranked grants, mostly OT2026 emergency applications
   (26A326, 26A274, 26A203, 26A124) plus 25-246, 25-238, 25-566, 25-965,
   25-1311, 24-1016, 24-6543. None concerned Remmer or extraneous jury
   information; used only as general context.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned recency-ranked denials, mostly OT2026 applications. Not probative.

## CourtListener MCP lookups

1. `search` (type `o`, court `ca6`, query "Maund Remmer extraneous", filed after
   2026-01-01) — **failed**: HTTP 429, "Rate limit exceeded: 300/hour", reset in
   about 846 seconds.
2. `search` (type `d`, court `scotus`, docket numbers 25-7403 / 25-7477 /
   25-1318) — **failed**: HTTP 429, same limit, reset in about 844 seconds.
3. Retry of the SCOTUS docket search after drafting the output — **failed**:
   HTTP 429, same limit, reset in about 657 seconds. Nothing live was read.

No REST fallback was used and no token was sought; the MCP server is the only
sanctioned path.

## Web searches

None.

## Committed base rates

`metrics/statpack.md`: modern discretionary-cert petitions by disposition;
cert petitions by relist count, by CVSG status and by salience band (paid scored
segment); SCOTUS cert petitions by Term; segment base rate by salience band
(sal-v4), pooling the bracketed `reached` figure for `baseline` over OT2017 to
OT2024.
