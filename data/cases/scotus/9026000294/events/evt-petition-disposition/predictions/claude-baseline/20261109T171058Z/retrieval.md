# Retrieval

- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-294.html`: live docket matches the snapshot. Last entry: Nov 09 2026, "DISTRIBUTED for Conference of 11/13/2026."
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-292.html`: companion Havlish docket. Shows the Oct 30 motion for leave to file a supplemental brief and the Nov 9 redistribution for 11/13.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`. Stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. Returned recent generic granted priors; none on point.
- An earlier `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` ran in the same shell. Its output was cut off in my view, so I don't know what it returned. I re-ran without `--era`.
- `metrics/statpack.md` read for the salience-band, relist-count, CVSG and amicus-count cuts.
- No CourtListener MCP calls.
