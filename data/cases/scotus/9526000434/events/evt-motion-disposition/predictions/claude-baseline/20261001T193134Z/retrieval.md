# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `fedcourts query --court scotus --include-applications --era 2020s --limit 12` — `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
2. `fedcourts query --court scotus --include-applications --era 2020s --disposition granted --limit 8` — `ranged corpus reads: 0 GET(s), 0 byte(s)`
3. `fedcourts query --court scotus --include-applications --era 2020s --limit 60` (summarized substantive rows: disposition, response requested, referral, amicus, pro se heuristic) — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
4. Same command as 3, re-read to print the full row for 26A397 (*Givey v. Givey*) — `ranged corpus reads: 0 GET(s), 0 byte(s)`
5. `fedcourts query --court scotus --include-open --include-applications --era 2020s --limit 400` (scan for Givey dockets and 26-153; found 26A397 denied and 26A331 extension granted) — `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
6. Same command as 5, re-read for 26A331's application kind — `ranged corpus reads: 0 GET(s), 0 byte(s)`
7. `fedcourts query --court scotus --include-open --era 2020s --limit 1500` — refused by the service (limit must be ≤ 500); no transfer line
8. `fedcourts query --court scotus --include-open --era 2020s --limit 500` (scan for 26-153; not found) — `ranged corpus reads: 34 GET(s), 8912896 byte(s)`

Base rates: `metrics/statpack.md`, section "The interim docket (applications)".

## CourtListener MCP

1. `search` type=d, q="Givey", court=ca3 → three Third Circuit dockets (23-2330, 25-3575, 26-1067)
2. `call_endpoint` docket-entries, docket=72136425 (CA3 26-1067) → 5 docketing entries
3. `call_endpoint` docket-entries, docket=72090988 (CA3 25-3575) → 3 docketing entries
4. `search` type=d, q="Givey", court=paed/pamd/pawd → no relevant hit
5. `search` type=o, q="Givey" → PA Supreme Court cluster 10319975 (*Givey v. Sunday*, 2025) among unrelated hits
6. `search` type=d, court=scotus, docket_number=26-153 → no results
7. `search` type=o, q="Givey", court=pa/pacommwct/pasuperct → no results
8. `search` type=r, q="Givey", docket_number=2:25-cv-00943 → E.D. Pa. docket 69662514 (*Givey v. Bondi*, § 1983)
9. `call_endpoint` docket-entries, docket=67917572 (CA3 23-2330, *Givey v. DOJ*) → briefing and submission entries from 2023
10. `call_endpoint` docket-entries, docket=69662514 (E.D. Pa.) → 12(b)(1) dismissal order of 2025-12-30 and later entries without text
11. `search` type=o, q="Givey", court=ca3/paed, filed_after 2023 → no results
12. `get_endpoint_item` clusters/10319975 → empty summary fields

No web searches. Nothing retrieved concerned this application's own disposition.
