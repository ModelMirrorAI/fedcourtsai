# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   Returned recency-ranked recent SCOTUS matters (mostly 26A-series applications,
   all at 0 distributions). Used for shape only; no text filter exists on this
   surface, so nothing topic-matched came back.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   Returned recent granted applications plus three granted OT2025 cert petitions
   (25-246, 25-238, 25-566) carrying 3, 22, and 17 distributions respectively.

## CourtListener MCP lookups

1. `search` (type `o`, court `ca9`, q "Crites-Bachert Providence") — **failed,
   HTTP 429 rate limit (300/hour; retry in ~862 s)**. Not retried.
2. `search` (type `o`, q `"360bbb-3" "informed consent" "private right of action"
   vaccine`, filed after 2021-01-01) — **failed, same 429**. Not retried.

No REST fallback was attempted. No web searches were made.

## Committed base rates

`metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
"by originating circuit", "by relist count", "by CVSG status", "by salience
band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band
(sal-v4)" (pooled OT2017-OT2024 `baseline` bracketed `reached` figures).
