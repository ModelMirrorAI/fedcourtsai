# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-09-17.json`, `record/documents/documents.json`, `record/documents/petition.txt`, `record/documents/questions-presented.txt`, the event definition, and the committed `metrics/statpack.md` (salience-band Term table, relist, CVSG, circuit and per-Term cuts).

## CourtListener MCP (2 calls)

1. `search` (type `o`, court `ca6`, q "Rubicon Real Estate Holdings Pontiac") — one hit: *Rubicon Real Estate Holdings v. City of Pontiac, Mich.*, No. 25-1631, filed 2026-06-18, status Published, judges Griffin, Larsen, Readler (cluster 10877275).
2. `call_endpoint` `clusters` (id 10877275, fields id/case_name/sub_opinions/judges/precedential_status/date_filed) — one sub-opinion listed, precedential status Published.

Neither call touched this case's Supreme Court docket or any post-docketing material; both concern the decision below, which predates the snapshot.

## Corpus tooling

No `fedcourts query` or `open-events` calls were made (no structured filter fit the case class; see `reasoning.md`). No `ranged corpus reads` line to record.

## Web search

None.
