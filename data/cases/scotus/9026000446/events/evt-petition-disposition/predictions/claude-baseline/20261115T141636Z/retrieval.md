# Retrieval log

- `metrics/statpack.md` — read the salience-band table (sal-v8), "Segment base rate by salience band", and the relist-count cut (paid scored segment).
- `uv run fedcourts query --help` — read the interface.
- `uv run fedcourts query --court scotus --disposition granted --era modern` — usage error (unknown era `modern`); no rows.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — `ranged corpus reads: 30 GET(s), 7798784 byte(s)`; returned five recent granted dockets (generic; none on this question). Not relied on.
- No CourtListener MCP calls and no web searches.
