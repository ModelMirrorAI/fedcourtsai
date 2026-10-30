# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era roberts` — usage/help output only (no rows; re-issued with `--limit`).
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 27 GET(s), 7077888 byte(s)`; five recent granted priors (several SG petitions); used only as context.
- CourtListener MCP `search` (type o, court ca10, q "Daley Baltazar") — failed: HTTP 429 rate limit exceeded.
- WebSearch "Daley v. Baltazar Tenth Circuit 24-1191" — found the SCOTUSblog case page for No. 26-146 and the citation Daley v. Ceja, 158 F.4th 1152 (10th Cir. Nov. 3, 2025).
- WebFetch https://www.scotusblog.com/cases/baltazar-v-daley/ — issue: whether EAJA's waiver for a "civil action" covers immigration-detention habeas; petition pending, response due Nov. 23, 2026 after extension. No disposition.
- WebSearch "\"Daley v. Ceja\" Tenth Circuit 2025 immigration detention" — press coverage of the Tenth Circuit holding (EAJA authorizes fees in immigration habeas; fee award affirmed).
- Read `metrics/statpack.md` (salience band table, relist and CVSG cuts).
