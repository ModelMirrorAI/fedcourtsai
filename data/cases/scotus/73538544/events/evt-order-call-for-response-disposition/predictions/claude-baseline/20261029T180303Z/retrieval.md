# Retrieval log

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: refused with a usage message (I did not pursue the flag error); no rows.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`
  - `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
  - Returned five recent GVR rows (e.g. scotus/73317900, scotus/73500268, scotus/73500579). Used only to confirm the GVR route is common on the live docket; none is on point.
- Read the committed `metrics/statpack.md` (salience band table, sal-v4).
- No CourtListener MCP calls, and no web searches.
