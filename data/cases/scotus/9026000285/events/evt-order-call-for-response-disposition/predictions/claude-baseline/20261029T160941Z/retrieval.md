# Retrieval log

- `uv run fedcourts query --help`: usage text.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`:
  refused (unknown era 'modern'). The vocabulary was printed.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`:
  `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. Five recent granted rows came back
  (government and election cases), none on point.
- `uv run fedcourts query --court scotus --citation '601 U.S. 330' --limit 3`:
  `ranged corpus reads: 7 GET(s), 1835008 byte(s)`. Empty, with a note that the
  citation column is sparse.
- `uv run fedcourts query --court scotus --docket-number 25A1338`:
  `ranged corpus reads: 9 GET(s), 2359296 byte(s)`. This is the petitioner's
  time-extension application, granted 2026-06-04.
- Read the committed `metrics/statpack.md` (band, relist, CVSG and circuit cuts).
- WebFetch of the supremecourt.gov docket page for 26-285. Entries run through
  2026-10-19: a response-time extension to 2026-11-18 was granted, and no disposition
  is entered.
- No CourtListener MCP calls.
