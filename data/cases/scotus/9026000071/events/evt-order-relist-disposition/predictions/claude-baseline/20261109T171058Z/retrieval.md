# Retrieval log
- WebFetch https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-828.html returned the Nwauzor docket: CVSG 2026-05-18, US amicus brief 2026-09-15, supplemental briefs 2026-09-29, distributed for 11/6 and then for 11/13. No disposition shown.
- `uv run fedcourts query --court scotus --docket-number 25-828` printed `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. It returned the Nwauzor row: cvsg_date 2026-05-18, no grant/deny dates, D. John Sauer for the United States.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 3` printed `ranged corpus reads: 33 GET(s), 8650752 byte(s)`. It returned unrelated GVR priors, used only for shape.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3` was a usage error (unknown era 'modern') and returned no rows.
- Read `metrics/statpack.md` for the relist-count cut.
- No CourtListener MCP calls.
