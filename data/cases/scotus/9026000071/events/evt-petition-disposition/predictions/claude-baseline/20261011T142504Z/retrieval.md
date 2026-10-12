# Retrieval

- `metrics/statpack.md` (committed): salience-band table (sal-v4), relist-count and CVSG cuts.
- CourtListener MCP `search` (type=d, court=scotus, q=`"GEO Group" Nwauzor`) — 0 results.
- `uv run fedcourts query --court scotus --q "GEO Group Nwauzor"` — rejected: `--q` is not an option, so no lookup ran and no `ranged corpus reads` line was printed.
