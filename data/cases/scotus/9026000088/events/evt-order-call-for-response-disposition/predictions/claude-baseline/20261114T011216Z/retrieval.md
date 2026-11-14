# Retrieval log

- `uv run fedcourts query --help` — read the flag surface.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 8` — usage error (`modern` is not an era token); returned the interface description only.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — `ranged corpus reads: 33 GET(s), 8585216 byte(s)`; five recent granted rows (government-petitioner and other matters), none on point; used only as shape.
- `uv run fedcourts query --court scotus --docket-number 23-926` — `ranged corpus reads: 18 GET(s), 4718592 byte(s)`; No on E v. Chiu row (on-communication donor disclaimer petition).
- `uv run fedcourts query --court scotus --docket-number 21-890` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`; Gaspee Project v. Mederos: denied 2022-04-25, distribution_count 3.
- `metrics/statpack.md` — modern cert dispositions, relist, CVSG, amicus-count and salience-band sections, per-Term band table.
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-88.html` (forward mode, the Court's own docket): entries after the snapshot — response time extended to Nov. 30, 2026 for all respondents (Sept. 16–17); four amicus briefs filed Sept. 30, 2026 (Nonprofit Alliance Foundation; Protect the First Foundation et al.; Cato Institute; Mountain States Legal Foundation). No disposition.
- No CourtListener MCP calls; no web searches.
