# Retrieval log

- WebFetch https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-118.html: the live docket matched the snapshot (latest entry: DISTRIBUTED for Conference of 11/13/2026; no disposition).
- WebFetch https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-116.html: the companion Caster cert-before-judgment docket has the same distribution path, still pending.
- WebFetch of the appellees' motion to dismiss PDF (26-118, Sept 18, 2026). The fetch summary failed, so I extracted the saved PDF with `uv run fedcourts pdf-text`. Its argument: the PI applies only to the Nov 3, 2026 election, so the appeal is or will be moot, and summary reversal is inappropriate.
- `uv run fedcourts query --court scotus --docket-number 25-273`: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. The prior Singleton appeal is labeled `gvr`.
- The same query again, parsed: `ranged corpus reads: 0 GET(s), 0 byte(s)`.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 3`: usage error (unknown era); no transfer line.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 3`: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`. Generic GVR priors, not directly used.
- Read metrics/statpack.md (relist-count, CVSG and salience-band cuts).
- No CourtListener MCP calls.
