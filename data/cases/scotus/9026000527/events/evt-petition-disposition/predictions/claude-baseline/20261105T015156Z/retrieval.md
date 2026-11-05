# Retrieval
- `uv run fedcourts query --help`
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` → usage error (unknown era 'modern'); no reads.
- `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 5` → no rows returned. stderr: `ranged corpus reads: 995 GET(s), 260440064 byte(s)`
- Read the committed `metrics/statpack.md` (salience band table, sal-v6).
- No CourtListener MCP or web lookups.
