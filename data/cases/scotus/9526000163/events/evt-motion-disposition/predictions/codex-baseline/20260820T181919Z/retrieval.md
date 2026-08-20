# Retrieval

- Read the committed `metrics/statpack.md`, “The interim docket (applications).” For OT2026, the strictly-prior pool is OT2025 (16/178) plus OT2024 (14/47): 30 grants among 225 resolved substantive applications.
- Ran `.venv/bin/fedcourts query --court scotus --limit 50`. Transfer report: `ranged corpus reads: 16 GET(s), 4194304 byte(s)`.
- Ran `.venv/bin/fedcourts query --court scotus --limit 100`. Transfer report: `ranged corpus reads: 16 GET(s), 4194304 byte(s)`. The broad results included recent pro se private-civil application denials; no lookup targeted this case.
- CourtListener MCP `search`: RECAP, Fifth Circuit, docket `26-30022`, party `Gilmore` (query `cc9a6256`). This identified *Gilmore v. Walmart*, lower-court docket ID 73507998.
- CourtListener MCP `get_endpoint_schema`: inspected the `docket-entries` endpoint fields.
- CourtListener MCP `call_endpoint`: read docket-entry dates, numbers, and descriptions for lower-court docket 73507998 (called twice, once to inspect and once to extract the relevant procedural entries; the first query was `d5c8de8a`).
- CourtListener MCP `search`: RECAP, docket `5:20-cv-01589`, party `Gilmore` (query `78979212`). This identified the underlying Western District of Louisiana employment-discrimination action.
- No web search was used, and no retrieval targeted the Supreme Court disposition or later Supreme Court docket history.
