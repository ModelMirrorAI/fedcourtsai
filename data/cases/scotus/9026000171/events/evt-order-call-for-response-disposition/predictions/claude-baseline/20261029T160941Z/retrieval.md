# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5`
  — usage error (`--era` value not accepted as given); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  — `ranged corpus reads: 27 GET(s), 7077888 byte(s)`; returned recent OT2025/26
  grants (none IDEA-related); used only as general context.
- Read committed `metrics/statpack.md` (salience band table, relist and amicus cuts).

No CourtListener MCP or web retrieval.
