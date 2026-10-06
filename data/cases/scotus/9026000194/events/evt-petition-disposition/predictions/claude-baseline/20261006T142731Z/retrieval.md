# Retrieval log

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  - stderr: `ranged corpus reads: 48 GET(s), 12451840 byte(s)`
  - Returned 15 recency-ranked granted SCOTUS rows, mostly emergency applications and federal-petitioner cases (none with a response-requested-after-waiver posture comparable to this one). Used for shape only; no number rests on it.

## CourtListener MCP lookups

- `search` (type `d`, court `scotus`, docket number `26-194`) to confirm the live docket state beyond the provisioned snapshot. **Failed**: HTTP 429, "Rate limit exceeded: 1400/day", expected available in about 53 minutes. Not retried; per the prompt contract the cell proceeded on the provisioned inputs and corpus tooling.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Modern cert petitions by originating circuit" (ca2 row), and "Segment base rate by salience band (sal-v4)" pooled over OT2017 to OT2025 for the `baseline` bracketed `reached` figure.

## Web searches

None.
