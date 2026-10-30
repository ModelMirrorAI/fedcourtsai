# Retrieval log

- `uv run fedcourts query --court scotus --citation "590 U.S. 45" --limit 3`
  — `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; returned no rows, with a
  `note:` that only 200 SCOTUS rows carry reporter citations.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
  — usage error (`modern` is not an era token); no reads reported.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — `ranged corpus reads: 24 GET(s), 6291456 byte(s)`; five recent granted
  dockets, none related to patent review; not relied on.
- Read committed `metrics/statpack.md` (salience-band, relist, CVSG,
  originating-circuit cuts).

No CourtListener MCP or web calls.
