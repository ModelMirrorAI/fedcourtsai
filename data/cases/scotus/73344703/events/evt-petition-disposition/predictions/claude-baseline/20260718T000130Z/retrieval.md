# Retrieval log

## Corpus lookups (fedcourts CLI)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   — recent granted SCOTUS priors, to see what grant-side dockets look like
   (multiple distributions, CVSG, specialist/SG involvement, high salience).
   Transfer line: `ranged corpus reads: 146 GET(s), 38273024 byte(s)`.

## Base rates

- Read the committed `metrics/statpack.md` and `metrics/statpack.json`
  (Term 2025 overall and per-fee-class cert rates, relist-count buckets, CVSG
  buckets, originating-court tables). The salience-band table named in the
  prompt is not present in this statpack version; anchored on the paid
  fee-class rate instead.

## CourtListener MCP

1. `search` (type=docket, court=scotus, docket_number=25-1285) — a single
   confirmatory lookup of this docket's current state. It failed with
   HTTP 429 (daily rate limit exhausted upstream). Not retried; proceeded on
   the provisioned snapshot (one day old) per the degradation rule.

## Web searches

None.
