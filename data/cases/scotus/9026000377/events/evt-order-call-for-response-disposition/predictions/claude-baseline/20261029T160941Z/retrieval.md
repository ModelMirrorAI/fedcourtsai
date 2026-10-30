# Retrieval log

- Read the committed `metrics/statpack.md`: the modern-cert, originating-circuit,
  relist, CVSG, amicus and salience-band sections, and the sal-v4 segment table.
- `uv run fedcourts query --court scotus --disposition granted --era modern --citation "597 U.S. 450" --limit 5`.
  Refused: usage error, unknown era `modern`.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`.
  Refused: the same usage error.
- `uv run fedcourts query --court scotus --citation "597 U.S. 450" --limit 3`
  - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
  - No rows came back. A note said the citations column is sparse: only 200
    SCOTUS rows carry any citation.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - `ranged corpus reads: 24 GET(s), 6291456 byte(s)`
  - Returned recent OT2025/OT2026 grants. None was an analogue, so none was
    used.
- No CourtListener MCP calls and no web searches.
