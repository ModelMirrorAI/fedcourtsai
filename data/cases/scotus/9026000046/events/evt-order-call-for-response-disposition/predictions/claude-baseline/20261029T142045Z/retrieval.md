# Retrieval log

- **WebFetch**: `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-46.html`
  (live docket, forward mode). It returned the snapshot's entries plus 2026-09-25:
  a motion to extend the time to respond to 2026-11-23, and 2026-09-28: the
  motion granted. There is no disposition.
- **Corpus**: `uv run fedcourts query --court scotus --docket-number 25-238`, to read
  the *Viramontes v. Cook County* row (granted 2026-06-30, 22 distributions, no
  merits decision yet).
  `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
- **Corpus**: `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`.
  It was rejected with a usage error (unknown era `modern`).
- **Corpus**: `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5`.
  It returned five recent GVR priors (none of them Second Amendment cases).
  `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
- **Corpus**: `uv run fedcourts query --court scotus --docket-number 25-238`, re-run to
  print the row's fields (stderr was not captured on that run).
- **Committed base rates**: `metrics/statpack.md` (the sal-v4 band table, plus the relist,
  CVSG and amicus cuts).
- No CourtListener MCP calls.
