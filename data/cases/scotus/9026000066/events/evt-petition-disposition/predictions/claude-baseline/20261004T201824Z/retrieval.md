# Retrieval log

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition denied`
  stderr: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
  Returned recent denied SCOTUS rows ranked by recency, mostly emergency applications; not informative for this cert petition's profile.

## CourtListener MCP lookups

1. `search` type=o, court=arizctapp, q=`"Smith" "2 CA-CV 2025-0101"`, filed_after=2026-01-01 → 0 results.
2. `search` type=d, court=scotus, docket_number=`26-66` → 0 results.
3. `search` type=o, court=arizctapp, q=`Smith marriage dissolution "Rule 77" transcripts presumption`, filed 2026-01-15 to 2026-01-25 → 0 results.
4. `search` type=d, court=scotus, q=`Michelet` → 0 results.

No web searches. No result surfaced this case's disposition.

## Committed base rates

`metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "by CVSG status (paid scored segment)", "Modern cert petitions by originating circuit", "Petitions by originating court (incl. state courts)", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (baseline `reached` pooled over 2017–2025).
