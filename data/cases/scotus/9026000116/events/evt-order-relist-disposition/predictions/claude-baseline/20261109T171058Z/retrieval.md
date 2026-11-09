# Retrieval
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-117.html`: the companion Milligan docket. It shows a motion to dismiss or affirm and distributions for 10/16, 11/6 and 11/13, identical to this docket. Nothing post-dates this docket's state.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: printed usage/help text (no rows); re-issued below.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`. Returned recent GVR priors (e.g., Cid v. United States, Monsanto v. Dennis), none on point.
- Read `metrics/statpack.md` (relist-count cut, salience-band table).
