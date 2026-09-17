# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation '145 S. Ct. 11' --citation '145 S. Ct. 1959' --citation '141 S. Ct. 160'`
   stderr: `ranged corpus reads: 1357 GET(s), 355532800 byte(s)`
   Result: no rows; printed `note: citations filter: 200 of 590880 rows in scope (scotus) carry citation data …`.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   Result: ~20 rows of 2020s grants and substantive applications (e.g. Chaney v. United States, 24-6543, distribution_count 5, granted 2026-06-29). Read for shape only; no case-specific signal.

## CourtListener MCP

3. `search` type=d court=scotus case_name="Hadley v. City of South Bend" — 0 results.
4. `search` type=d court=scotus case_name="Baker v. City of McKinney" — 0 results.
5. `search` type=d court=scotus case_name="Slaybaugh v. Rutherford County" — 0 results.
6. `call_endpoint` docket-entries docket=73281647 — 0 results (SCOTUS dockets carry no entries on CourtListener).
7. `call_endpoint` dockets court=scotus docket_number=25-1158 — Amy Hadley v. City of South Bend, id 73281642, filed 2026-04-08, not terminated, cert dates null.
8. `call_endpoint` dockets court=scotus docket_number=23-1363 — Vicki Baker v. City of McKinney, id 69409453, filed 2024-07-02, cert dates null (stale; the petition was denied in October 2024).
9. `call_endpoint` dockets court=scotus docket_number=24-708 — returned an unrelated docket (Iqbal); Slaybaugh's number is 24-755.
10. `search` type=d court=scotus q="Hadley South Bend" — 0 results.
11. `get_endpoint_item` dockets 73281647 — this case: filed 2026-04-09, date_terminated null, cert dates null, date_modified 2026-06-24. Consistent with the snapshot; not decided.
12. `call_endpoint` docket-entries docket=69409453 (Baker) — 0 results.

## Web search (engine-surfaced)

13. "Slaybaugh v. Rutherford County certiorari denied relisted Supreme Court takings SWAT" — IJ case page, SCOTUSblog case file, the 24-755 docket page; petition filed 2025-01-14, denied 2025-04-28. Sources: https://ij.org/case/slaybaugh-swat-appeal/ , https://www.scotusblog.com/cases/case-files/slaybaugh-v-rutherford-county-tennessee/ , https://www.supremecourt.gov/docket/docketfiles/html/public/24-755.html
14. "\"Pena v. City of Los Angeles\" certiorari 25-1163 …" — SCOTUSblog case page confirms distributed for conference 9/28/2026; IJ case page; the CA9 opinion PDF. Sources: https://www.scotusblog.com/cases/pena-v-city-of-los-angeles/ , https://ij.org/case/los-angeles-swat-destruction/
15. "\"Hadley v. City of South Bend\" Supreme Court petition 25-1158 conference" — SCOTUSblog case page: distributed for conference September 28, 2026; the 25-1158 docket page. Sources: https://www.scotusblog.com/cases/hadley-v-city-of-south-bend/ , https://www.supremecourt.gov/docket/docketfiles/html/public/25-1158.html

Nothing retrieved disclosed this case's disposition. Also read: `metrics/statpack.md` (committed base rates).
