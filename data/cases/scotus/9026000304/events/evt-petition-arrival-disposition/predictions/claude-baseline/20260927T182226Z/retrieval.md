# Retrieval log

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 9026000304 --event evt-petition-arrival-disposition --role predictor` (path resolution; no transfer line).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 25 GET(s), 6422528 byte(s)`
  Result: eight rows, mostly OT2026 emergency-application dockets resolved within days of filing plus two OT2025 petition rows, all with null captions and bands. Not informative for this cell; recorded for completeness.

## Committed base rates

- `metrics/statpack.md`: "Segment base rate by salience band (sal-v4)" (federal column, OT2017 to OT2025, pooled by hand), "Cert petitions by salience band", "Cert petitions by relist count", "Cert petitions by CVSG status", "Modern cert petitions by originating circuit" (ca9 row).

## CourtListener MCP

1. `search` type=o, court=ca9, q=`Chattah "Vacancies Reform Act" "first assistant"`, filed after 2026-01-01. One hit: United States v. Salazar Del Real, No. 25-6475, filed 2026-08-17, published. Confirms the decision below.
2. `search` type=o, court=ca3, q=`Giraud "Vacancies Reform Act" Habba`, filed after 2025-06-01. One hit: United States v. Julien Giraud, Jr., No. 25-2635, filed 2025-12-01, published.
3. `search` type=o, court=ca2, q=`"Grand Jury Subpoenas" "Vacancies Reform Act" "first assistant"`, filed after 2026-06-01. One hit: In re Grand Jury Subpoenas to the Office of the New York State Attorney General, No. 26-156, filed 2026-08-21, published.
4. `search` type=d, court=scotus, docket_number=26-304. No results; this docket is not in RECAP, so I did not see any post-snapshot docket activity.
5. `search` type=o, courts ca1/ca4/ca5/ca6/ca7/ca8/ca10/ca11/cadc, q=`"Vacancies Reform Act" "United States Attorney" "first assistant" 3345`, filed after 2025-06-01. No results; no other circuit has a published post-2025 ruling on the question that this search surfaced.

No web searches. Nothing retrieved disclosed this petition's disposition.
