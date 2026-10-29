# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 24-427` (Hittle v. City of Stockton). Returned: denied 2025-03-10, 5 distributions.
  stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 3`. Refused: `modern` is not an era token. No rows returned.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`. Returned five recent grant-family rows, none on point.
  stderr: `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
- WebSearch (standard): "Supreme Court grants certiorari McDonnell Douglas summary judgment 2026". Returned supremecourt.gov PDFs for several pending petitions on the same issue (26-80, 26-385, 26-448, 26-5352, 25-945) and this case's own petition. Nothing showed this case's disposition or any grant on the issue.
- Read the committed `metrics/statpack.md`.
- No CourtListener MCP calls.
