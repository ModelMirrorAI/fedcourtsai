# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 25-1359`. Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Companion row: ca3, distributed for 2026-09-28, distribution_count 1, no CVSG, no disposition, last_live_polled 2026-10-25.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`. Refused because `modern` is not an era token, so there was no transfer line. I re-issued it with `--era 2020s`.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`. Stderr: `ranged corpus reads: 24 GET(s), 6291456 byte(s)`. Five recent grants came back as general context: 26A512, 26-12, 26-204, 26A476 and 25-1103. None is on point.
- WebFetch of `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-1359.html` (companion docket). Shows: waiver and South Carolina amicus on 2026-07-08, distributed 2026-07-15, response requested 2026-07-29, response time extended to 2026-11-02. No disposition.
- Read `metrics/statpack.md` (base rates).
- No CourtListener MCP calls.
