# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` failed with a usage error (bad `--era` value); no rows returned.
- `uv run fedcourts query --court scotus --disposition denied --era roberts --limit 3` failed the same way.
- `uv run fedcourts query --court scotus --disposition denied --limit 3` returned 3 rows: recent application-docket denials, not useful as priors. stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
- WebFetch of the supremecourt.gov docket page for No. 25-1303 returned the full docket through the Oct 28, 2026 distribution for the Nov 13, 2026 conference. No disposition has issued.
- Read the committed `metrics/statpack.md` for base rates.
- No CourtListener MCP calls.
