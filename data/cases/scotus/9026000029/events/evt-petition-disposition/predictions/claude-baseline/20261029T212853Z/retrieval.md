# Retrieval log

Corpus (via the cell's corpus service):

1. `uv run fedcourts query --court scotus --citation "582 U.S. 255" --citation "592 U.S. 351" --limit 5`
   — `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. No rows. The note says only
   200 SCOTUS rows carry reporter cites (a sparse column).
2. `uv run fedcourts query --court scotus --disposition summary-reversal --limit 3`
   — `ranged corpus reads: 899 GET(s), 235536384 byte(s)`. No rows.

Committed base rates: read `metrics/statpack.md`, covering the modern-cert, relist, CVSG,
amicus and salience-band sections and the sal-v4 segment band table.

No CourtListener MCP calls and no web searches.
