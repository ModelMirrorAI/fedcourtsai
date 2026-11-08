# Retrieval

- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/25-1246.html returned the
  companion docket. It shows a record request on Aug 11 2026, a motion to defer, a reschedule,
  and a distribution for the 12/4/2026 conference. No disposition.
- `uv run fedcourts query --docket-number 25-1246` failed with a usage error
  (it needs `--court`; I reissued it).
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 3` failed:
  unknown era token.
- `uv run fedcourts query --court scotus --docket-number 25-1246 --include-open` returned
  `ranged corpus reads: 17 GET(s), 4456448 byte(s)`. The companion row is open,
  distribution_count 3, capital, ca5.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3` returned
  `ranged corpus reads: 20 GET(s), 5242880 byte(s)`. These were generic recent grants, of little
  use.
- `uv run fedcourts query --help`
- Read `metrics/statpack.md` for the salience-band, relist and CVSG cuts.
- No CourtListener MCP calls.
