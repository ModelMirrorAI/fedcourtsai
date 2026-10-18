# Retrieval log

- Committed `metrics/statpack.md`: sal-v4 salience-band table, relist-count and CVSG cuts.
- `uv run fedcourts query --help`: help text only, no corpus query run, so no `ranged corpus reads` line.
  The corpus query cannot look up a named companion case.
- CourtListener MCP `search` (type d, scotus, docket_number 25-34): 0 results.
- CourtListener MCP `search` (type d, scotus, q "Continental Finance"): 0 results.
- CourtListener MCP `search` (type o, scotus, q "Continental Finance" arbitration consideration, filed after 2025-06-01): 0 results.
- CourtListener MCP `search` (type d, scotus, q Johnson Continental, filed after 2025-06-01): 0 results.
- CourtListener MCP `call_endpoint` dockets (court scotus, docket_number 25-34): found docket 73272764, *Continental Finance Co. v. Johnson*, filed 2025-07-10, not terminated.
- CourtListener MCP `call_endpoint` docket-entries (docket 73272764): 0 entries.
- CourtListener MCP `call_endpoint` dockets (id 73272764): no cert-granted or denied dates recorded.
- Web search: "Continental Finance" v. Johnson 25-34 … returned background on the Fourth Circuit opinion.
- Web search: Supreme Court "25-34" Continental Finance Johnson … surfaced the supremecourt.gov joint stipulation to dismiss No. 25-34, filed 2026-05-05.
  This is the companion case, not this case. Nothing about No. 25-311's disposition surfaced.
