# Retrieval log

- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-199.html: HISA v. National Horsemen's (CA5 23-10520), petition Aug 10 2026, responses from challengers, distributed for 12/4/2026.
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/25-1325.html: Oklahoma v. United States (CA6), distributed for 10/9/2026, rescheduled Sep 21, distributed for 12/4/2026.
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-335.html: matches the snapshot. Last entry is the Nov 4 distribution for 12/4/2026; no disposition yet.
- `uv run fedcourts query --court scotus --docket-number 24-433` → `ranged corpus reads: 17 GET(s), 4456448 byte(s)`: the prior-round HISA petition, disposition `gvr`.
- `uv run fedcourts query --court scotus --citation "606 U.S. 656"` → `ranged corpus reads: 10 GET(s), 2621440 byte(s)`: no rows (a coverage note says the citation column is sparse).
- Read `metrics/statpack.md` (salience band table, sal-v8).
- No CourtListener MCP calls.
