# Retrieval Log

## Local Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --help`
   - Inspected CLI options and structured filter flags for `fedcourts query`.
2. `uv run fedcourts query --court scotus --party "Jack Daniel" --party "Booking.com" --party "Elster" --party "Abitron" --party "Dewberry" --limit 20`
   - Failed (`Exit Code: 2`): `No such option: --party` (returned CLI flag documentation).
3. `uv run fedcourts query --court scotus --stage merits --limit 25`
   - Failed (`Exit Code: 2`): `No such option: --stage` (returned CLI flag documentation).
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 25`
   - `ranged corpus reads: 57 GET(s), 14876672 byte(s)`
   - Returned 25 granted 2020s SCOTUS dockets (recent OT2025/OT2026 grants and interim applications).
5. `uv run fedcourts query --court scotus --disposition granted --decided-before 2026 --limit 20`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 20 granted SCOTUS dockets, including the corpus metadata row for `scotus/72483489` (`date_cert_granted: "2026-06-29"`, `cvsg_date: "2025-10-06"`, `merits_decided: null`, `merits_judgment: null`) and peer June 2026 grants.
6. `uv run fedcourts query --court scotus --disposition granted --decided-before 2025 --limit 15`
   - `ranged corpus reads: 46 GET(s), 12058624 byte(s)`
   - Returned 15 OT2024-numbered granted SCOTUS dockets (granted between Sept. 2025 and June 2026).
7. `uv run fedcourts query --court scotus --disposition granted --era 2010s --limit 10`
   - `ranged corpus reads: 281 GET(s), 73596928 byte(s)`
   - Returned 10 resolved granted SCOTUS merits cases from the 2010s/early-2020s cohort with `merits_judgment` labels (`reversed`, `vacated`, `affirmed`), including *Hughes v. Northwestern University* (`scotus/61595192`, CVSG followed by grant and `merits_judgment: "vacated"`) and *United States v. Cooley* (`scotus/59755752`, `merits_judgment: "vacated"`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", q=""Hana Financial" OR "Booking.com" OR "Jack Daniel's" OR "Dewberry" OR "Elster" OR "Abitron"", filed_after="2014-01-01", filed_before="2026-11-05", num_results=20, fields=["caseName", "citation", "dateFiled", "judge", "cluster_id", "opinions", "snippet"])`
   - Returned 32 matching SCOTUS opinions (20 shown), including *USPTO v. Booking.com B.V.*, *Hana Financial, Inc. v. Hana Bank*, *Jack Daniel's Properties, Inc. v. VIP Products LLC*, *Dewberry Group, Inc. v. Dewberry Engineers Inc.*, *Abitron Austria GmbH v. Hetronic Int'l, Inc.*, and *Vidal v. Elster*.
2. `mcp_courtlistener_search(type="o", court="scotus", q=""Village at Lakeridge" AND ("mixed question" OR "standard of review")", filed_after="2018-01-01", filed_before="2026-11-05", num_results=20, fields=["caseName", "citation", "dateFiled", "judge", "cluster_id", "opinions", "snippet"])`
   - Returned 16 matching SCOTUS opinions on mixed-question standards of review, including *U.S. Bank N.A. v. Village at Lakeridge, LLC*, *Bufkin v. Collins*, *Wilkinson v. Garland*, *Google LLC v. Oracle America, Inc.*, and *Monasky v. Taglieri*.
3. `mcp_courtlistener_read_document(opinion_id=2771751, chunk_index=0)`
   - Read syllabus/opening of *Hana Financial, Inc. v. Hana Bank*, 574 U.S. 418 (2015) (Sotomayor, J., 9–0).
4. `mcp_courtlistener_read_document(opinion_id=9400443, chunk_index=0)` and `chunk_index=1`
   - Read syllabus, disposition (`vacated and remanded`), and vote/concurrence lineup of *Jack Daniel's Properties, Inc. v. VIP Products LLC*, 599 U.S. 140 (2023) (Kagan, J., 9–0; concurrences by Sotomayor and Gorsuch).
5. `mcp_courtlistener_read_document(opinion_id=10806546, chunk_index=0)`
   - Read syllabus, disposition (`vacated and remanded`), and vote/concurrence lineup of *Dewberry Group, Inc. v. Dewberry Engineers Inc.*, 604 U.S. 321 (2025) (Kagan, J., 9–0; concurrence by Sotomayor).
6. `mcp_courtlistener_read_document(opinion_id=4251727, chunk_index=0)`
   - Read syllabus, disposition, and vote/concurrence lineup of *U.S. Bank N.A. v. Village at Lakeridge, LLC*, 583 U.S. 387 (2018) (Kagan, J., 9–0; concurrences by Kennedy, Sotomayor, and Gorsuch).
7. `mcp_courtlistener_read_document(opinion_id=10816961, chunk_index=0)` and `chunk_index=1`
   - Read syllabus and vote lineup of *Bufkin v. Collins*, 604 U.S. 369 (2025) (Thomas, J., 7–2; Jackson, J., dissenting, joined by Gorsuch, J.).

## Web Searches / Fetches

- None attempted.
