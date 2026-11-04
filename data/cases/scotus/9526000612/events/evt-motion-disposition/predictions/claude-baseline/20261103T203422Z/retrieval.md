# Retrieval

- `uv run fedcourts query --help` (usage)
- `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 5` → usage error (flag not accepted), no rows
- `uv run fedcourts query --court scotus --docket-number 26A612` → this docket's own row (substantive application, 0 amicus). `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5` → usage error, no rows
- `uv run fedcourts query --court scotus --disposition denied --limit 5` → 5 denied substantive applications from OT2026 (mostly pro se, e.g. 26A606, 26A613, 26A617, 26A618, 26A499). `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
- Read `metrics/statpack.md` (interim section) and `metrics/statpack.json` (`interim.terms` finer counts)
- WebFetch: supremecourt.gov docket page for 26A612 → entries for Oct 20 (application submitted to the Chief Justice) and Oct 30, 2026 (docketed); no disposition
- No CourtListener MCP calls.
