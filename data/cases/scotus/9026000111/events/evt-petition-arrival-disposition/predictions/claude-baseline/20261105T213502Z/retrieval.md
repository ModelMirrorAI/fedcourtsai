# Retrieval

- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-111.html`. It returned the live docket: two extensions of the time to respond (to Sept. 23, then Dec. 7, 2026), with no distribution or disposition.
- `uv run fedcourts query --docket-number 25-417` was refused with a usage error (`--court` required).
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` was refused with a usage error (unknown era).
- `uv run fedcourts query --court scotus --docket-number 25-417 --include-open`: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`. It confirmed that Nielsen v. Watanabe is an open docket with the SG participating.
- `uv run fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 5`: `ranged corpus reads: 993 GET(s), 260112384 byte(s)`. I only skimmed the output.
- Read `metrics/statpack.md` (salience-band table and modern-cert disposition table).
- No CourtListener MCP calls.
