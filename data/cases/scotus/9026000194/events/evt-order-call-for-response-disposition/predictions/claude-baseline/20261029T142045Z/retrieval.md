# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (no `--era modern` value accepted / help printed); re-issued without it.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  - `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
  - Returned recent granted SCOTUS rows (mostly federal-government cases); not closely comparable, used only as general context.
- `uv run fedcourts query --help` (read usage).
- WebFetch of the supremecourt.gov docket page for No. 26-194: showed post-snapshot entries (extension to Oct 21, 2026; amicus brief of the Official Committee of Unsecured Creditors of Vanderbilt Minerals, LLC on Sep 21; brief in opposition on Oct 21). No disposition.
- Committed `metrics/statpack.md` read for base rates.
- No CourtListener MCP calls.
