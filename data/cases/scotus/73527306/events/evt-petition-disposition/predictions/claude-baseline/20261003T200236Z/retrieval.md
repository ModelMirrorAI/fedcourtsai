# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 73527306 --event evt-petition-disposition --role predictor` (path resolution only).
- `uv run fedcourts query --court scotus --disposition summary-reversal --limit 12` — no rows returned. stderr: `ranged corpus reads: 777 GET(s), 203554816 byte(s)`.
- `uv run fedcourts query --court scotus --disposition gvr --limit 8` — 8 rows (recent GVRs, mostly end-of-OT2025 holds). stderr: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`.
- `uv run fedcourts query --court scotus --limit 40` — 40 rows, recent SCOTUS dockets (mostly applications), used only to see the shape of recent rows. stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`.

## Statpack (`metrics/statpack.md`, committed)

Modern discretionary-cert petitions by disposition; by originating circuit
(ca8 row); by relist count and by CVSG status (paid scored segment); the
per-Term table; and the segment base rate by salience band (sal-v4),
pooling the `elevated` bracketed `reached` figures over Terms 2017–2024.

## CourtListener MCP

1. `search` (opinions, court ca8, q "Marks v. Bauer") — located Marks I (107 F.4th 840, cluster 10000688) and Marks II (filed 2026-02-12, cluster 10790532). Did not read either body; the petition appendix carried Marks II in full.
2. `call_endpoint dockets` (court scotus, docket_number 24-616) — found the prior petition's docket (id 72485497, filed 2024-12-05).
3. `call_endpoint docket-entries` (docket 72485497) — zero entries held by CourtListener.
4. `search` (opinions, court scotus, q "Zorn v. Linton", filed after 2025-06-01) — found the 2026-03-23 per curiam, No. 25-297 (opinion 11280281).
5. `read_document` (opinion 11280281, chunks 0–1 of 8) — read the opening and Part II of Zorn v. Linton to confirm it is a per curiam summary reversal granting qualified immunity in a protest-arrest case.

No web searches. Nothing retrieved concerns this petition's own disposition.
