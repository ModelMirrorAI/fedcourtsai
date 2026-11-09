# Retrieval log
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-292.html`: live docket. Entries are identical to the snapshot (last entry: 11/9 distributed for 11/13). No CVSG, no call for a response.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (`--era modern` not accepted / output showed the help text). No rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`: returned 5 recent granted SCOTUS rows (generic priors, not on point). stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`.
- Read the committed `metrics/statpack.md` (modern cert, relist, CVSG, amicus and salience-band cuts).
- No CourtListener MCP calls.
