# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — stderr: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. Returned five recent
  granted SCOTUS dockets (government applications and petitions), none on point.
  I did not use them.
- `uv run fedcourts query --help` (usage only, no corpus read).
- Read the committed `metrics/statpack.md` (band table, relist and amicus cuts).
- No CourtListener MCP calls and no web searches.
