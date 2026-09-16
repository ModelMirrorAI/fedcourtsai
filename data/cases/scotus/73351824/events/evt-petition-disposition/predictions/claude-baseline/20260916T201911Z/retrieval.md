# Retrieval log

## Provisioned inputs (read, not retrieval)

- `record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`
- `metrics/statpack.md` (committed base rates)

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "599 U.S. 255"` → no rows.
   stderr: `ranged corpus reads: 1357 GET(s), 355532800 byte(s)`; note: citations filter covers 200 of 590895 scotus rows.
2. `uv run fedcourts query --court scotus --citation "570 U.S. 637"` → no rows.
   stderr: `ranged corpus reads: 1352 GET(s), 354222080 byte(s)`; same coverage note.

## CourtListener MCP lookups

1. `search` type=docket, court=scotus, q=`"Indian Child Welfare Act"`, filed_after 2023-06-15 → 0 results.
2. `search` type=opinion, court=scotus, q=`"Indian Child Welfare Act" AND (certiorari OR "petition for writ")`, filed_after 2023-06-16 → 0 results.
3. `search` type=opinion, court=scotus, q=`Brackeen ICWA`, filed_after 2023-07-01 → 0 results.

## Web fetches (forward cell; documents linked from the provisioned snapshot)

1. `https://www.supremecourt.gov/DocketPDF/25/25-1287/420147/20260826110750485_25-1287%20Brief%20in%20Opposition.pdf` (brief in opposition, Aug 26, 2026; 46 pages, text extracted locally with pypdf).
2. `https://www.supremecourt.gov/DocketPDF/25/25-1287/423145/20260904144316236_25-1287_Reply%20Brief.pdf` (reply brief, Sep 4, 2026; 19 pages, text extracted locally).

No search surfaced this petition's disposition; the case is pending for the September 28, 2026 conference.
