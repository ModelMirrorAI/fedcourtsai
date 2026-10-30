# Retrieval log

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: refused with a usage error (the `--era` value was not accepted); no rows came back.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`: `ranged corpus reads: 31 GET(s), 8060928 byte(s)`. It returned 5 recent GVR priors (e.g., Burford German Funding v. financialright; Monsanto v. Dennis), none of them NLRA or Loper Bright cases, so they did not inform the forecast.
- `uv run fedcourts query --help`: read the help text.
- `metrics/statpack.md`: the committed base rates (sal-v4 band table and the relist, CVSG and circuit cuts).
- No CourtListener MCP calls and no web searches.
