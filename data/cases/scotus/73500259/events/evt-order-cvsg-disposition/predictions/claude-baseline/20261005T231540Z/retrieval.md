# Retrieval log

## Corpus queries (`fedcourts query`, service backend)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  — stderr: `ranged corpus reads: 27 GET(s), 6946816 byte(s)`. Returned
  recency-ranked granted rows (mostly federal-party and application rows); no
  CVSG-conditioned priors, so it did not inform the anchor.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  — stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache). Returned
  recency-ranked denials from the October 5, 2026 order list; not informative
  for this cell.

## CourtListener MCP lookups

- `search` (type `o`, court `ca9`, q `"Seagate" "NHK Spring" FTAIA`) — located
  the decision below: *Seagate Technology LLC v. NHK Spring Co., Ltd.*,
  No. 24-4470, filed 2026-01-08, published, cluster 10771069.
- `search` (type `d`, court `scotus`, q `"Motorola Mobility" "AU Optronics"`) —
  no SCOTUS docket indexed; the Motorola cert history was not retrievable here.
- `get_endpoint_item` (clusters, 10771069) — no panel, judges, or syllabus
  metadata on the cluster; one combined sub-opinion.
- `get_endpoint_item` (opinions, 11237654) — no author string; not per curiam.

## Committed base rates

- `metrics/statpack.md`: modern discretionary-cert base rate; relist-count and
  CVSG cuts (paid scored segment); `sal-v4` segment base rate by salience band,
  pooled over Terms 2017–2024 for the `high` band.

No web searches. Nothing about this petition's own disposition was sought or
surfaced.
