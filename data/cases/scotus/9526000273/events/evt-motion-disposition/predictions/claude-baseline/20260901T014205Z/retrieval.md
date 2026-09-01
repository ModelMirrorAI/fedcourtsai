# Retrieval log

Beyond the provisioned inputs (`event.yaml`, `record/context.json`, the
2026-09-01 snapshot) and the committed `metrics/statpack.md` (interim-docket
section), I ran three corpus queries through the cell's corpus service:

1. `uv run fedcourts query --court scotus --limit 15`
   — `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
2. `uv run fedcourts query --court scotus --limit 3` (field inspection)
   — `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
3. `uv run fedcourts query --court scotus --limit 200`
   — `ranged corpus reads: 36 GET(s), 9437184 byte(s)`

Query 3 was filtered client-side for `capital_case` and
`application_kind == "substantive"`: 52 substantive applications (50 denied,
2 granted) and 12 capital rows (all denied), including five capital stay
applications — 26A209, 26A175, 26A119, 26A121, 26A54 — all denied. Newest
resolved prior returned: 2026-08-31 (corpus vintage evidence; `corpus-info`
needs a local blob and is not runnable in this cell).

No CourtListener MCP lookups and no web searches: the application was ripe for
disposition at snapshot time, so live retrieval about this case risked surfacing
its own outcome (see `reasoning.md`).
