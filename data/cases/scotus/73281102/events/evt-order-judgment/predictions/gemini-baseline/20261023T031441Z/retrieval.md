# Retrieval Log

## 1. Corpus Lookups (`fedcourts`)

- `uv run fedcourts paths --court "scotus" --docket "73281102" --event "evt-order-judgment" --role predictor`
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  - `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 25`
  - `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
- `uv run fedcourts query --court scotus --disposition granted --decided-before 2025 --limit 10`
  - `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
- `uv run fedcourts query --court scotus --disposition granted --era 2010s --limit 5`
  - `ranged corpus reads: 136 GET(s), 35651584 byte(s)`

## 2. CourtListener MCP Lookups

- `mcp_courtlistener_search(type="o", case_name="Fortner v. Eischen", fields=["caseName", "court_id", "dateFiled", "citation", "docketNumber", "snippet"], num_results=5)` — verified the Eighth Circuit's March 13, 2026 decision in *Anthony Fortner v. B. Eischen, Warden*, No. 24-3596, cited in the cert-stage briefing.
- `mcp_courtlistener_search(type="o", case_name="Melot v. Bergami", fields=["caseName", "court_id", "dateFiled", "citation", "docketNumber", "snippet"], num_results=5)` — verified the Fifth Circuit's decision in *Billy Melot v. Thomas Bergami*, 970 F.3d 596 (5th Cir. 2020), relied upon by the Fifth Circuit panel below.

## 3. Web Searches

- None.
