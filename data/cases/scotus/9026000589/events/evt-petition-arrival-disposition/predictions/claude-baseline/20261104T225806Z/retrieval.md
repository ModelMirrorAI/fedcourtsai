# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 30 GET(s), 7864320 byte(s)`; returned recent granted SCOTUS rows, mostly SG petitions (used for general shape only).
- `uv run fedcourts query --court scotus --docket-number 26-210` — `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; returned the Trump v. Thakur row (companion Tucker Act petition cited in the petition).
- An earlier `uv run fedcourts query ... --era modern --limit 5` attempt printed help/usage instead of rows. No results.
- `uv run fedcourts query --help`, which printed usage only.
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-210.html (Trump v. Thakur docket). It showed petition filed Aug 18, 2026, BIO Oct 19, reply Oct 27, and distribution for the Nov 13, 2026 conference.
- Read `metrics/statpack.md`, the salience-band table (sal-v6).
