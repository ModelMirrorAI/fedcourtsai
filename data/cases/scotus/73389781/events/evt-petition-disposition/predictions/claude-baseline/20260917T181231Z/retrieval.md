# Retrieval log

Provisioned inputs read: `record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, `record/documents/brief-in-opposition.txt`, and the event definition `events/evt-petition-disposition/event.yaml`.

Base rates: the committed `metrics/statpack.md` (Modern discretionary-cert petitions by disposition; Cert petitions by relist count, by CVSG status, by salience band; SCOTUS cert petitions by Term; Segment base rate by salience band (sal-v4)).

Corpus lookups:

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned the eight most recent 2020s grants (substantive applications and cert grants on unrelated subjects). Not topically relevant; not used in the forecast.

CourtListener MCP lookups: none. The snapshot is dated the day before this run and the conference has not occurred, so I did not query the live docket.

Web searches: none.
