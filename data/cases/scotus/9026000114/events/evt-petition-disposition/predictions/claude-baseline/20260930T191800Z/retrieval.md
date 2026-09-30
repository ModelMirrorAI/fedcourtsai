# Retrieval log

## Corpus lookups (`fedcourts query`, read-only via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation '140 S. Ct. 994' --citation '589 U.S. 248'`
   - stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - stderr note: citations filter sparse (only 200 scotus rows carry any cite).
   - Returned the prior trip, scotus/16446939 (No. 18-877, Allen v. Cooper),
     disposition `granted`, distribution_count 3, no CVSG, originating ca4.
2. `uv run fedcourts query --court scotus --citation '514 U.S. 35'`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - stderr note: same sparse-cite coverage note; no row for Swint.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   - stderr: `ranged corpus reads: 40 GET(s), 10354688 byte(s)`
   - Used only for the shape of recent grants (distribution counts on granted
     paid petitions); no doctrinally similar prior surfaced.

## CourtListener MCP lookups

1. `search` (type `o`, court `ca4`, filed after 2025-06-01, query
   "Allen v. Stein pendent appellate jurisdiction Blackbeard Queen Anne's Revenge")
   → one hit: Frederick Allen v. Joshua Stein, No. 24-1954, filed 2026-01-23,
   status Published, cluster 10779194, opinion 11245804.
2. `read_document` opinion 11245804, chunks 2 and 3 (procedural history).
3. `read_document` opinion 11245804, chunks 4 and 5 (jurisdiction section,
   parties' positions, Swint framework).
4. `read_document` opinion 11245804, chunk 6 (application of the two Swint
   prongs; "sole and only seed"; exercise of discretion).

## Base rates

`metrics/statpack.md`: modern discretionary-cert base rates; relist-count,
CVSG, and salience-band cuts; the per-Term "Segment base rate by salience band
(sal-v4)" table, pooled over OT2017 through OT2025 for the `elevated` band's
bracketed `reached` figure.

No web searches. Nothing under `data/qp-topics/` was read. No search surfaced
this petition's disposition.
