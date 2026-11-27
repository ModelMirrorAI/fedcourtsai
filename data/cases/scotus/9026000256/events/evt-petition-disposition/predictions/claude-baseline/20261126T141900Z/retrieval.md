# Retrieval

- `uv run fedcourts query --help` — read the interface.
- `uv run fedcourts query --court scotus --docket-number 26-257` — `ranged corpus reads: 20 GET(s), 5242880 byte(s)`. Returned the *Nathan v. Alamo Heights ISD* row: pending, one distribution, conference 2026-12-11.
- `uv run fedcourts query --court scotus --docket-number 25-1360` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Returned the *Brumley v. Roake* row: pending, three distributions, conference 2026-12-11.
- `uv run fedcourts query --court scotus --disposition granted --era modern` — rejected (`Unknown era 'modern'`); no rows, not re-issued.
- `metrics/statpack.md` — "Segment base rate by salience band (sal-v9)" table, baseline column.
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-257.html` — *Nathan* docket: petition Aug 17, three amicus briefs, BIO Nov 10, reply Nov 20, distributed Nov 24 for Dec 11; no order on the petition.
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-1360.html` — *Roake* docket: waiver, response requested Jul 28, BIO Oct 19, distributed for Dec 4, rescheduled Nov 5, distributed Nov 24 for Dec 11; no order on the petition.
- No CourtListener MCP calls and no web searches.
