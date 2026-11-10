# Retrieval log
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (unknown era 'modern'); no rows returned.
- `uv run fedcourts query --docket-number 25-466`: usage error (needs --court); no rows returned.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. Returned recent granted priors, used for shape only.
- Read `metrics/statpack.md` (modern cert, circuit, relist, CVSG, amicus, band tables).
- WebSearch (standard): "Sripetch v. SEC Supreme Court decision disgorgement 2026". Confirmed the decision of June 4, 2026: unanimous, Gorsuch, J.; no pecuniary-loss requirement. No result concerned this case's disposition.
