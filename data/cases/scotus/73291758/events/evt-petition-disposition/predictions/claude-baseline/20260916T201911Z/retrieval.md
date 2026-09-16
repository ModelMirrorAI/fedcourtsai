# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-09-16.json`,
`record/documents/documents.json`, `record/documents/petition.txt`,
`record/documents/questions-presented.txt`, the event definition, and the
committed `metrics/statpack.md` (modern discretionary-cert section, the
relist/CVSG/capital/band cuts, the per-Term table, and the sal-v4 segment
base-rate table).

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 8` →
  `ranged corpus reads: 7 GET(s), 1835008 byte(s)`. Returned eight
  recency-ranked 2020s rows (seven substantive applications and one dismissed
  IFP petition); none comparable to a pro se state protective-order petition,
  so they did not inform the number. No further filter retried.

## CourtListener MCP lookups (forward mode; unrestricted)

1. `get_endpoint_item` dockets/73291758 — docket 25-1245, filed 2026-05-04,
   `date_terminated` null, `date_modified` 2026-06-17. No disposition.
2. `call_endpoint` docket-entries?docket=73291758 — 0 results (CourtListener
   holds no entries for this SCOTUS docket).
3. `search` type=o, q=`Dittmer "order of protection"`, courts illappct/ill,
   filed after 2025-01-01 — 0 results.
4. `search` type=o, case_name=Dittmer, court illappct, filed after
   2025-06-01 — 0 results. The Illinois Appellate Court order below is not on
   CourtListener.

No web searches.
