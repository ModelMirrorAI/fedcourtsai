# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --limit 5` (an earlier attempt with `--era modern` added printed usage text and returned no rows)
  — `ranged corpus reads: 5 GET(s), 1310720 byte(s)`; returned recent denied OT2026 substantive applications (none capital), used only as shape.
- `uv run fedcourts query --docket-number 26-6013` — printed usage text; no row returned.
- Read `metrics/statpack.md` (interim docket section) and `metrics/statpack.json` (interim per-Term finer counts).
- No CourtListener MCP calls and no web searches.
