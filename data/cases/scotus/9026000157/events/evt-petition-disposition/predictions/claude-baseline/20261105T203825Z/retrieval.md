# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` returned a usage error (`modern` is not an era token).
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` returned `ranged corpus reads: 30 GET(s), 7864320 byte(s)`. It gave five recent granted SCOTUS rows, mostly federal-government cases, which I used only as general context.
- `metrics/statpack.md` (committed): read the modern cert, relist, CVSG, amicus and salience-band sections.
- WebSearch: "Supreme Court certiorari church autonomy neutral principles 2026 McRaney O'Connell petition". It surfaced this petition's PDF, *USCCB v. O'Connell* (No. 25-849) materials, and SCOTUSblog. It reported that O'Connell cert was denied May 26, 2026.
- WebSearch: "O'Connell Catholic Bishops certiorari denied May 2026 Alito dissent church autonomy". It confirmed the O'Connell denial (religionclause.blogspot.com, ncronline, christianpost, law360) and surfaced no report of a noted dissent.
- No CourtListener MCP calls.
- Nothing about this petition's own disposition surfaced.
