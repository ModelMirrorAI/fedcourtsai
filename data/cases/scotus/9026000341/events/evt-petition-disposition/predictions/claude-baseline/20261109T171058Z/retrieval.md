# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`. This printed the help text: the flag spelling was not accepted as written, so I re-issued the query without `--era`.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` printed `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. It returned recent granted SCOTUS priors (general context only, nothing on point).
- Read the committed `metrics/statpack.md` sections: modern cert dispositions, the originating-circuit cut, relist, CVSG and amicus cuts, the salience band table (sal-v8).
- No CourtListener MCP calls and no web searches.
