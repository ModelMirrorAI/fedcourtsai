# Retrieval log

Forward-mode cell; retrieval unrestricted. Nothing about this petition's
disposition was sought or surfaced (the next conference postdates the snapshot).

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned four interim applications and four recent grants (Jouppi v. Alaska,
  Viramontes v. Cook County, Grant v. Higgins, Grand v. University Heights);
  none is a comparable government-speech prior, so it informed nothing beyond
  confirming the corpus carries recent OT2025 grants.
- One earlier invocation with a malformed flag (`--include-open=false`) errored
  before reading the corpus and returned no rows.
- `metrics/statpack.md` (committed): modern cert by disposition, relist-count
  and CVSG cuts, originating-circuit cut, and the per-Term "Segment base rate
  by salience band (sal-v4)" table, pooled over OT2017 through OT2024.

## CourtListener MCP

1. `search` (type opinion, court ca9, case name "Khatibi v. Hawkins"): two
   published clusters, the July 25, 2025 panel opinion (cluster 10641179) and
   the December 29, 2025 en banc denial (cluster 10766015).
2. `search` (type opinion, court scotus, case name "Chiles v. Salazar"):
   confirmed the decision date March 31, 2026, No. 24-539, opinion by Justice
   Gorsuch.
3. `get_endpoint_item` clusters 10641179: metadata carried no panel field.
4. `call_endpoint` opinions filtered to cluster 10641179: opinion id 11107766,
   38 pages, no author string.
5. `search_document` on opinion 11107766 for "Circuit Judge": panel of
   Tashima, Nguyen, and Mendoza, opinion by Judge Nguyen.

No web searches.
