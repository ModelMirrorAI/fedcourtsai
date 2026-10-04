# Retrieval log

Forward cell; retrieval unrestricted. Beyond the provisioned inputs:

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   Returned 25-1131 (2 distributions), 25-1349 (1 distribution), and three
   September 2026 application dockets (26A428, 26-426, 26A406). Not used as an
   anchor; recorded for shape only.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned five September–October 2026 application dockets (26A447, 26A370,
   26A434, 26A437, 26A382). Not used as an anchor.

## CourtListener MCP lookups

3. `search` type=o, court=ca5, q=`"Merritt" "Texas Farm Bureau" overtime`,
   filed_after 2025-06-01. One result: Merritt v. Texas Farm Bureau,
   No. 24-50127, filed 2026-02-06, status Published. Used to confirm the
   decision below is a published opinion.
4. `search` type=o across ca1–ca11 and cadc, q=`FLSA "suffer or permit"
   overtime "actual or constructive knowledge" employer`, filed_after
   2018-01-01. **Failed: HTTP 429 rate limit exceeded (300/hour), reset in
   ~1140 s.** Not retried.
5. `search` type=d, court=scotus, q=`"Fair Labor Standards Act" overtime`,
   filed_after 2025-10-01. **Failed: HTTP 429 rate limit exceeded, reset in
   ~1139 s.** Not retried.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "Modern cert petitions by originating circuit" (ca5 row),
  "Cert petitions by relist count (paid scored segment)", "Cert petitions by
  CVSG status (paid scored segment)", "SCOTUS cert petitions by Term", and
  "Segment base rate by salience band (sal-v4)" (pooled `baseline` bracketed
  `reached` figure over OT2017–OT2025).

No web searches.
