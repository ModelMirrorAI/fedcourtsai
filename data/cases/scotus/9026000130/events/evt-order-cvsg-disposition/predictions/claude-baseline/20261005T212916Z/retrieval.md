# Retrieval log

Provisioned inputs read: `record/snapshots/2026-10-05.json`, `record/context.json`, `record/documents/documents.json`, `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, the event's `event.yaml`, and the committed `metrics/statpack.md` (modern cert, relist, CVSG, and sal-v4 salience band sections).

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   `ranged corpus reads: 16 GET(s), 4063232 byte(s)`
   Returned recent granted SCOTUS rows (mostly federal-party cert grants and substantive applications from OT2026); no CVSG-specific filter exists, so this served only as a sanity check of the live slice and did not shape the number.
2. `uv run fedcourts query --court scotus --citation '587 U.S. 1051' --citation '552 U.S. 1095'`
   `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   Empty; the CLI printed a `note:` that only 200 scotus rows carry reporter citations, so the two prior Teck denials are not locatable this way.

## CourtListener MCP lookups

3. `search` type `d`, court `scotus`, docket_number `06-1188` — 0 results (Supreme Court dockets not indexed).
4. `search` type `d`, court `scotus`, docket_number `18-1160` — 0 results.
5. `search` type `o`, court `ca9`, q `"Teck Cominco" "natural resource damages" cultural`, filed after 2025-01-01 — 1 result: *Confederated Tribes of the Colville Reservation v. Teck Cominco Metals Ltd*, filed 2025-09-03 (cluster 10665433), confirming the decision below; its text was not opened.

No web searches. Nothing retrieved concerned this petition's disposition or any post-snapshot entry on this docket.
