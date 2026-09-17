# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --text "..." --limit 8` — rejected:
   `query` takes no free-text argument (structured filters only). No corpus
   read occurred.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   — `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned five recent
   granted rows (four substantive applications and one cert docket, Jouppi v.
   Alaska). Used only to confirm the query surface works; none of the rows is
   a Padilla-type prior and none informed the number.

## CourtListener MCP

1. `search` (type `o`, court `ca3`, filed after 2025-01-01, query
   `Patel "Sixth Amendment" "collateral consequences" "False Claims Act" Padilla`)
   — **failed**: HTTP 429, rate limit exceeded (300/hour), retry available in
   about 855 seconds. No further MCP calls attempted; no REST fallback used.

## Web searches

None.

## Base rates

`metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
"Modern cert petitions by originating circuit" (ca3 row), "Cert petitions by
relist count (paid scored segment)", "Cert petitions by CVSG status (paid
scored segment)", "SCOTUS cert petitions by Term", and "Segment base rate by
salience band (sal-v4)" (baseline column, OT2017 to OT2024 bracketed
`reached` figures pooled).
