# Retrieval log

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5`. This failed
  with a usage error: the help text was printed and no rows came back.
- `uv run fedcourts query --court scotus --disposition denied --limit 3`, which printed
  `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. It returned three recent OT2025 denials (Guardado v.
  Florida, Guardado v. Comerford, Lopez Jaime v. Blanche). They are generic and not used beyond confirming the surface.
- I read `metrics/statpack.md`: the relist-count, CVSG and amicus cuts (paid scored segment) and the
  sal-v8 segment band table.
- No CourtListener MCP calls and no web searches.
