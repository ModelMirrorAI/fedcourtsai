# Retrieval log — claude-baseline, 26A428, evt-brief-response-disposition

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `fedcourts query --court scotus --disposition granted --limit 40`
   → `ranged corpus reads: 52 GET(s), 13565952 byte(s)`
2. `fedcourts query --court scotus --disposition denied --limit 40`
   → `ranged corpus reads: 0 GET(s), 0 byte(s)`
3. `fedcourts query --court scotus --disposition granted --limit 40` (re-run to print full rows)
   → `ranged corpus reads: 0 GET(s), 0 byte(s)`
4. `fedcourts query --court scotus --disposition granted --include-applications --limit 200`
   → `ranged corpus reads: 0 GET(s), 0 byte(s)`
5. `fedcourts query --court scotus --disposition denied --include-applications --limit 200`
   → `ranged corpus reads: 0 GET(s), 0 byte(s)`
6. `fedcourts query --court scotus --disposition dismissed --include-applications --limit 200`
   → `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
7. `fedcourts query --court scotus --disposition withdrawn --include-applications --limit 200`
   → `ranged corpus reads: 758 GET(s), 198574080 byte(s)`
8. `fedcourts query --court scotus --disposition granted --limit 40` (detail on 25A1235 / 25A1314)
   → `ranged corpus reads: 23 GET(s), 6029312 byte(s)`

Used from these: twelve denied capital prisoner applications (Terms 2026), two
withdrawn capital applications, and one granted capital State application to
vacate a Fifth Circuit stay (Guerrero v. Busby, 25A1235). No `--full` hydration.

## Base rates

`metrics/statpack.md`, "The interim docket (applications)": pooled Terms 2024–2025,
31 granted / 296 resolved substantive ≈ 10.5%.

## CourtListener MCP

1. `search` type=r court=ca6 docket_number=26-5864 → In re: Christa Pike, docket 74871499.
2. `search` type=r court=tned docket_number=1:12-cv-00035 entries after 2026-09-01 → Pike v. Johns, docket 5240271 (no entry detail returned; not used further).
3. `search` type=r court=ca6 docket_number=26-5864 fields=recap_documents, dateTerminated → stay order (doc 10-2), not terminated as of 2026-09-30T14:34Z.
4. `read_document` recap_document_id=495590629 → full text of the Sixth Circuit's published stay order and Griffin dissent.

No web searches. The 26A428 Supreme Court docket was not looked up.
