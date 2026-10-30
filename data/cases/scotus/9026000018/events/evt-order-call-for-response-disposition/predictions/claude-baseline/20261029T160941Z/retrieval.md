# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (`--era` value not accepted in this form); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` → `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. Returned recent granted SCOTUS dockets (all federal-government or applications, none on mootness/PLRA). Background only.
- WebFetch of the supremecourt.gov docket page for No. 26-18. The docket showed the response deadline extended to Oct 2, 2026, the BIO filed Oct 2, the reply filed Oct 20, and a distribution for the 11/6/2026 conference. No disposition.
- `metrics/statpack.md` (committed): salience-band table (sal-v4), relist-count and CVSG cuts.
- No CourtListener MCP calls.
