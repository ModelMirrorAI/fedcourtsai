# Retrieval log

## Provisioned inputs read
- `record/context.json`, `record/snapshots/2026-09-18.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt` (full text, 49 pages, not truncated), `events/evt-petition-disposition/event.yaml`.
- Committed `metrics/statpack.md`: *Modern discretionary-cert petitions by disposition*, *Modern cert petitions by originating circuit*, *Cert petitions by relist count (paid scored segment)*, *Cert petitions by CVSG status (paid scored segment)*, *Cert petitions by salience band*, *SCOTUS cert petitions by Term*, *Segment base rate by salience band (sal-v4)*.

## Corpus lookups (`fedcourts query`)
1. `uv run fedcourts query --court scotus --limit 8 "pro se petition APA administrative record supplementation debarment military installation Fourth Circuit federal respondent waiver"` — rejected as a usage error (the command takes no free-text argument); no transfer line, nothing read.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5` — stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned four 2026 emergency applications (26A326, 26A274, 26A203, 26A124) and Jouppi v. Alaska (25-246, granted after 3 distributions). None analogous; not used to move the number.

## CourtListener MCP lookups
1. `search` type=`o`, court=`ca4`, docket_number=`24-1166` — 0 results.
2. `search` type=`o`, court=`ca4`, q=`"Defense Logistics Agency" Jones debarment`, filed_after=2025-01-01 — 0 results.

The Fourth Circuit opinion below is not indexed on CourtListener; the decision was characterized from the petition's own description and the docket.

## Web searches
None.
