# Retrieval log

Corpus:
- `uv run fedcourts query --help` (usage only).
- `uv run fedcourts query --court scotus --docket-number 26-208` — returned the *Anibowei v. Blanche* row (CA5, distributed once for 2026-10-09, pending, ten amicus counsel listed). `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — five recent granted rows, none on this question; not used. `ranged corpus reads: 31 GET(s), 8060928 byte(s)`
- `metrics/statpack.md`: relist-count, CVSG, amicus-count, salience-band and per-Term band tables.

Web (forward mode):
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-208.html` — *Anibowei* docket: waiver Sept 14, amicus briefs Sept 15-18, distributed for Oct 9, response requested Sept 29, response time extended to Nov 30, 2026. Used.
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-604.html` — this docket; same five entries as the snapshot.

CourtListener MCP: not used. No web searches.
