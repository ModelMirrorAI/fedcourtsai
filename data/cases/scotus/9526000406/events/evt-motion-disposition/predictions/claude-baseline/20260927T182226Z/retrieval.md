# Retrieval log

## Corpus tooling

1. `uv run fedcourts query --court scotus --include-applications --disposition granted --era 2020s --limit 20`
   stderr: `ranged corpus reads: 7 GET(s), 1703936 byte(s)`
   Recent granted applications; almost all time-extension rows, plus DHS v. League
   of Women Voters (26A308) and People Not Politicians v. Onder (26A388).
2. `uv run fedcourts query --court scotus --include-applications --disposition denied --era 2020s --limit 12`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
3. `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 400`
   stderr: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   Filtered locally to substantive rows with the Solicitor General as applicant:
   five rows, three granted, one denied, one withdrawn; all five carry
   `referred_to_court: true` except the withdrawn one.
4. `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 1500`
   Rejected by the corpus service (limit must be <= 500); no rows, no transfer line.
5. An earlier `fedcourts query` invocation with a free-text argument was rejected
   before running (the command takes no positional search text).

Base rates: `metrics/statpack.md`, section "The interim docket (applications)".

## CourtListener MCP

- `search` type `d`, court `scotus`, docket_number `26A406`: 0 results (the
  application docket is not indexed there).

## Web

- WebSearch: `"D.V.D." Supreme Court stay application September 2026 third-country removals Justice Jackson`
- WebFetch: lawdork.com post "DOJ goes to SCOTUS to re-start rapid third-country removals" (Sept 24, 2026)
- WebFetch: reason.com/volokh post on Justice Jackson's handling of the administrative stay (Sept 24, 2026)
- WebFetch: supremecourt.gov docket 26A406 (live entries as of Sept 27, 2026: submission; response requested, due Sept 28)
- WebFetch: supremecourt.gov docket 24A1153 (the prior application in this case: response requested May 28, 2025; three amicus entries; referred and granted June 23, 2025; motion to clarify granted July 3, 2025)

None of the above disclosed this application's disposition; it is pending.
