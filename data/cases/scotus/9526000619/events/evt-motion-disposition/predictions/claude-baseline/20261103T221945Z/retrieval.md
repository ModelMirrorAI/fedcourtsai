# Retrieval log

- `uv run fedcourts query --court scotus --disposition denied --era roberts --include-applications --limit 5`: usage error (the flags were rejected and the help text was printed), no rows returned.
- `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 5`: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`. Returned recent denied applications, including several self-represented stay applications (e.g., Nichloson v. U.S. Bank). Used for shape only.
- `uv run fedcourts query --help`: read the usage text.
- `uv run fedcourts pdf-text record/documents/application.txt`: failed ("not a readable PDF"). The staged text is empty.
- WebFetch of the supremecourt.gov docket page for 26A619: same single entry (Oct 27, 2026 application submitted to The Chief Justice), docketed Oct 30, 2026. Nothing after it.
- Read `metrics/statpack.md` (interim section) and `metrics/statpack.json` (`interim.terms[].finer_*`).
- No CourtListener MCP calls.
