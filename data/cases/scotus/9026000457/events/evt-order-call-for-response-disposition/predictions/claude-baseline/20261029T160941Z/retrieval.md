# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 24-118`
  - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
  - Returned PhRMA v. McClain (Eighth Circuit Arkansas 340B case). Disposition `denied`, one distribution, no CVSG recorded.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3`
  - Refused: `modern` is not an era token (eras are decade tokens). No rows came back and I did not retry it.
- `uv run fedcourts query --court scotus --docket-number 24-118` (re-run to parse fields; stderr discarded)
- Read the committed `metrics/statpack.md`: the salience-band table, the CVSG cut and the amicus cut.

No CourtListener MCP calls and no web searches.
