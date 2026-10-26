# Retrieval Log (`retrieval.md`)

## 1. Corpus and Base-Rate Tooling (`fedcourts`)

- `uv run fedcourts segment-anchors --term 2025`
  - Retrieved pooled per-band segment base rates for docket Term 2025 (`sal-v4`, lookback 10, pooling OT2017–OT2024; `high` band `risk_set = 34.97%`, `n = 898`).
- `uv run fedcourts query --court scotus --docket-number 25-944 --limit 5`
  - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`

## 2. CourtListener MCP Lookups

- `mcp_courtlistener_search(type="o", case_name="Sodha v. Golubowski", fields=["caseName", "citation", "dateFiled", "court_id", "docketNumber", "cluster_id"], num_results=5)`
  - Confirmed the Ninth Circuit decision below (`Sodha v. Golubowski`, No. 24-1036, `cluster_id = 10663157`, filed `2025-08-29`).
- `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10663157, fields=["id", "case_name", "citations", "date_filed", "precedential_status", "judges"])`
  - Confirmed `precedential_status: "Published"` for the Ninth Circuit decision below.
