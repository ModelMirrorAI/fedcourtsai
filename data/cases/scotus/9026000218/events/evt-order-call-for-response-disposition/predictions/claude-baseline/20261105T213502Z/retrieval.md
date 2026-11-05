# Retrieval

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: usage error (the `--era` value was not accepted); no rows were returned.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`. It returned five recent GVR priors (e.g. Burford German Funding; Monsanto v. Dennis; Hobson v. United States), none on point; I used them only as a shape check.
- Read the committed `metrics/statpack.md` for the modern-cert disposition, relist, CVSG, amicus and salience-band tables.
- No CourtListener MCP calls and no web searches.
