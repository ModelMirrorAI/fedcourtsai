# Retrieval

- Consulted `metrics/statpack.md` and the 2025 paid-petition detail in `metrics/statpack.json` for modern cert, originating-circuit, relist, CVSG, Term, and fee-class base rates.
- Corpus lookup: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - `ranged corpus reads: 148 GET(s), 38731776 byte(s)`
  - The returned recent grants were used only as general conference/relist context; none was treated as a close case-level analog.
- CourtListener MCP opinion search: `type=o`, `q="\"inter partes review\" \"314(d)\" institution"`, `court=scotus`, `order_by="score desc"`, `num_results=5`, fields limited to identifying metadata and snippet. It returned *Thryv, Inc. v. Click-To-Call Technologies, LP*, *Cuozzo Speed Technologies, LLC v. Lee*, and *SAS Institute Inc. v. Iancu*, confirming the relevant Supreme Court doctrinal line identified in the provisioned briefs.

No web search was used, and no lookup sought this case's outcome or subsequent history.
