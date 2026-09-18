# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
  Returned eight recency-ranked rows, all September 2026 emergency
  applications (26A-series) plus one dismissed IFP petition; no comparable
  cert priors, so not used beyond confirming the tool's reach.

## CourtListener MCP

1. `search` (type `o`, court `ca5`, q "Endure Industries Vizient") — located
   the Fifth Circuit opinion, cluster 10773935, opinion 11240520, published,
   filed 2026-01-13, docket 24-10995.
2. `call_endpoint` `docket-entries` for docket 73500287 — returned zero
   entries (the SCOTUS docket carries no RECAP entries on CourtListener).
3. `read_document` opinion 11240520, chunk 0 — panel (Smith, Stewart,
   Ramirez), author Judge Smith, facts and procedural history.
4. `read_document` opinion 11240520, chunks 4–6 — the GPO Market analysis,
   footnote 7 (core-customer theory forfeited and non-binding), the Vizient
   DMS Market analysis, and the affirmance.
5. `get_endpoint_item` `dockets` 73500287 — `date_terminated: null`,
   `date_modified` 2026-07-16; confirms the docket is open with no filing
   after the amicus brief.

## Web searches

None.

## Provisioned inputs read

`record/context.json`, `record/snapshots/2026-09-18.json`,
`record/documents/documents.json`, `record/documents/petition.txt`,
`record/documents/questions-presented.txt`, the event definition, and
`metrics/statpack.md`.
