# Retrieval log

Corpus lookups:
- `uv run fedcourts query --court scotus --citation "489 U.S. 538" --limit 3`
  — `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; no rows (note: only
  200 SCOTUS rows carry any citation).
- `uv run fedcourts query --court scotus --disposition granted --citation "399 U.S. 66" --limit 3`
  — `ranged corpus reads: 0 GET(s), 0 byte(s)`; no rows (same sparse-citation note).
- `uv run fedcourts query --court scotus --era modern --disposition denied --limit 3`
  — refused as a usage error (`modern` is not an era token); no transfer line.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  — `ranged corpus reads: 24 GET(s), 6291456 byte(s)`; five unrelated recent
  grants, not used.

Committed base rates: `metrics/statpack.md` (modern cert, relist-count, CVSG,
amicus, salience-band and sal-v4 segment tables).

No CourtListener MCP calls and no web searches.
