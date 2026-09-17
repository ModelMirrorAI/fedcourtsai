# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  (default limit 20) — pulled a ranked set of granted 2020s SCOTUS priors to
  see the profile of granted petitions (counsel, SG participation). Used for
  shape only.
  - `ranged corpus reads: 47 GET(s), 12320768 byte(s)`

## CourtListener MCP

- `search` type=d, court=scotus, q=`"interactive process" AND ("Rehabilitation
  Act" OR "Americans with Disabilities Act")`, filed_after=2025-06-01 — 0
  results. Checked for a pending SCOTUS docket that could make this petition
  a hold candidate.
- `search` type=d, court=scotus, docket_number=25-1336 — 0 results
  (CourtListener carries no docket record for this petition).

## Base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "Modern cert petitions by originating circuit" (ca4 row),
  "Cert petitions by relist count (paid scored segment)", "Cert petitions by
  CVSG status (paid scored segment)", "SCOTUS cert petitions by Term", and
  "Segment base rate by salience band (sal-v4)" (baseline column, OT2017 to
  OT2024 pooled).

No web searches were run.
