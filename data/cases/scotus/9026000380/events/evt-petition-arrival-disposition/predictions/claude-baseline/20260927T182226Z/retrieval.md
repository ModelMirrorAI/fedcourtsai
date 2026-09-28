# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-09-21.json`,
`record/documents/documents.json`, `record/documents/questions-presented.txt`,
`record/documents/petition.txt`, the event's `event.yaml`, and the committed
`metrics/statpack.md` (modern discretionary-cert, relist, CVSG, salience band,
per-Term, and the sal-v4 segment base-rate tables).

## Corpus lookups (`fedcourts query`, through the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   — stderr: `ranged corpus reads: 49 GET(s), 12713984 byte(s)`. Returned
   recent substantive applications (e.g. DHS v. League of Women Voters, 26A308;
   People Not Politicians v. Onder, 26A388) ranked by recency; no comparable
   SG cert petition in the head of the list. Not used for the number.
2. `uv run fedcourts query --court scotus --citation "583 U.S. 281" --citation
   "590 U.S. 573" --citation "525 U.S. 471" --citation "589 U.S. 221"` —
   stderr: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`; empty result with
   the note that only 200 scotus rows carry any reporter citation (coverage
   gap, not absence).

## CourtListener MCP lookups

1. `search` type `o`, court `ca4`, q "Suri v. Trump", filed after 2026-07-01 —
   one hit: *Badar Suri v. Donald Trump*, No. 25-1560, filed 2026-07-23,
   Published. Confirms the decision below.
2. `search` type `d`, court `scotus`, q "Khalil", filed after 2026-06-01 — no
   results (CourtListener holds no SCOTUS docket for a Khalil petition).
3. `search` type `o`, court `ca3`, q "Khalil", filed after 2025-06-01 — three
   hits, including *Mahmoud Khalil v. President United States of America*,
   No. 25-2162, Published, filed 2026-01-15 and 2026-05-22. Confirms the
   Third Circuit side of the split as the petition describes it.

No web searches. Nothing retrieved concerned this case's own disposition.
