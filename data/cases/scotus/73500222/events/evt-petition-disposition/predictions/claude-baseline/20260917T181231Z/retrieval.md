# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   Returned eight recency-ranked resolved rows, mostly September 2026
   applications and denials; no Rule 54(d) or costs petition among them.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   stderr: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   Returned six recent grants (applications and two paid petitions); none
   comparable to this case.

## CourtListener MCP lookups (attempted, failed)

1. `search` (type opinions, federal courts of appeals) for the chilling-effect
   costs factor citing Stanley v. University of Southern California.
   Result: HTTP 429, rate limit exceeded (300/hour), available in ~537 s.
2. `search` (type dockets, court scotus, case_name Karsjens) for this
   litigation's prior Supreme Court dockets.
   Result: HTTP 429, same limit.

Neither call was retried; the cell proceeded on the provisioned inputs, the
corpus query results above, and `metrics/statpack.md`.

## Web searches

None.
