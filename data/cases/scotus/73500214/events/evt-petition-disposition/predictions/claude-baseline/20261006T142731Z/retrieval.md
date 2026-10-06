# Retrieval log

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7208960 byte(s)`. Returned eight
  recent granted rows with null captions; used only to confirm the tooling was
  live, not as evidence.

## CourtListener MCP lookups

- `search` type `d`, court `scotus`, docket_number `25-1350` (Flagstar Bank v.
  Kivett): failed, HTTP 429 rate limit exceeded (1400/day), retry available in
  about 62 minutes.
- `search` type `d`, court `scotus`, docket_number `25-1004` (Citizens Bank v.
  Conti): failed, same HTTP 429.

No further MCP calls were attempted; the cell proceeded on the provisioned
inputs and the committed statpack as the prompt directs on a degraded upstream.

## Web searches

None.

## Base rates

`metrics/statpack.md`: Segment base rate by salience band (sal-v4), `high`
column pooled over OT2017 to OT2024; Cert petitions by CVSG status and by relist
count (paid scored segment); Modern cert petitions by originating circuit.
