# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-10-08.json`, `record/documents/documents.json` (petition fetched with `empty_text: true`; `petition.txt` is empty), `events/evt-petition-disposition/event.yaml`, and the committed `metrics/statpack.md`.

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   `ranged corpus reads: 28 GET(s), 7274496 byte(s)`
   Returned eight recent granted rows (25-1131, 25-1349, 26-104, 26-426 and four 26A applications); used for shape only.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 6`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   Returned six recent denied rows (26A456, 26A459, 26A470, 25-1218, 25-1219, 25-7274); used for shape only.

## CourtListener MCP lookups

1. `search` (opinions, court ca8, q "Hauber Honkamp Krueger"): 0 results.
2. `search` (opinions, courts ca8/iasd/iand/ilnd/ilcd, q "Hauber", filed after 2024-01-01): 0 results.
3. `search` (RECAP, q "Hauber Honkamp"): found N.D. Iowa dockets 2:23-cv-01033 (Hauber v. Honkamp Krueger & Co., P.C., ADA, civil rights: jobs; docket id 68013931) and 2:22-cv-01029 (Honkamp Krueger & Co., PC v. Hauber; docket id 66672509).
4. `search` (dockets, court ca8, docket number 25-2561): 0 results through the search index.
5. `call_endpoint` docket-entries for docket 68013931 (newest 60 entries): the posture below, including the June 2, 2025 Rule 37(b)(2) dismissal with prejudice and $500 sanction, the Aug 4, 2025 pro se notice of appeal, the Eighth Circuit's March 23, 2026 affirmance, and the Aug 10, 2026 denial of post-judgment reconsideration motions.
6. `call_endpoint` docket-entries for docket 66672509: three entries with empty descriptions; nothing usable.
7. `call_endpoint` dockets (court ca8, docket number 25-2561): one row, "Ryan Hauber v. Honkamp Krueger & Co. PC", appeal from N.D. Iowa (Eastern); no nature of suit, no dates.
8. `search` (opinions, q "Honkamp", filed after 2025-06-01): two unrelated Eighth Circuit opinions; the Hauber opinion is not indexed.

No web searches. Nothing retrieved disclosed this petition's disposition.
