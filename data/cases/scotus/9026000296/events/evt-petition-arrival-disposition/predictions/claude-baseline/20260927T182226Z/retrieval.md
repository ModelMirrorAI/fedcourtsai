# Retrieval log

## Corpus lookups (`fedcourts query`, local corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   stderr: `ranged corpus reads: 11 GET(s), 2752512 byte(s)`
   Returned recent OT2025 substantive applications; not on point for a cert arrival cell and not used in the number.
2. `uv run fedcourts query --court scotus --era 2020s --limit 6`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   Same population; not used in the number.

(An initial attempt passing free text as a positional argument was rejected by the CLI and made no read.)

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition"; "Modern cert petitions by originating circuit" (ca9 row); "Cert petitions by relist count (paid scored segment)"; "Cert petitions by CVSG status (paid scored segment)"; "Cert petitions by salience band"; "SCOTUS cert petitions by Term"; "Segment base rate by salience band (sal-v4)" (baseline column, OT2017 to OT2025 pooled).

## CourtListener MCP lookups

1. `search` type=o, court=ca9, q=`"Lnu" Blanche attorney discipline suspension`, filed after 2026-05-01: found Lnu v. Blanche, No. 24-4790, filed 2026-06-03, cluster 10869591.
2. `search` type=o, court=scotus, q=`"In re Ruffalo" attorney suspension "court of appeals"`, filed after 1990: 0 results.
3. `search` type=d, court=scotus, docket_number=26-296: 0 results.
4. `call_endpoint` opinions, cluster=10869591 (plain text of the Ninth Circuit's June 3, 2026 disciplinary order): read for the panel's notice, hearing-waiver, and knowledge findings.
5. `call_endpoint` dockets, court=scotus, docket_number=26-296: 0 results (no post-snapshot docket entries seen).
6. `search` type=o, court=scotus, q=`Ruffalo disbarment OR suspension attorney "due process"`, filed after 1986: 3 results (Gray v. Netherland, Green v. Bock Laundry, Frazier v. Heebe), none a review of a court of appeals' attorney discipline order.

## Web searches

None.
