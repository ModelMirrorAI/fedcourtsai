# Retrieval log

1. `uv run fedcourts query --help` — read the interface.
2. `uv run fedcourts query --court scotus --docket-number 26-348` — returned the companion row (United States v. Office of the New York State Attorney General, from ca2, pending, distribution_count 0 as of its 2026-11-16 poll). stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
3. `uv run fedcourts query --court scotus --disposition granted --era modern` — rejected: `Unknown era 'modern'`; no rows returned, not re-issued.
4. WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-348.html` — the Court's docket for 26-348: BIO filed Nov. 2, 2026; reply Nov. 16; distributed Nov. 17 for the conference of Dec. 4, 2026; no amicus briefs.
5. Read `metrics/statpack.md` (salience-band table, relist-count and amicus-count cuts).

No CourtListener MCP calls. No web searches.
