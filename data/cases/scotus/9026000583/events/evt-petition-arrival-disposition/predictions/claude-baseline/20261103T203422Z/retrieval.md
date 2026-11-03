# Retrieval log

- `uv run fedcourts query --help`: usage.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5` returned `ranged corpus reads: 29 GET(s), 7602176 byte(s)`. All five recent grants were counseled (mostly SG or government) petitions. That confirms the contrast with a pro se paid petition.
- Read `metrics/statpack.md`, the "Segment base rate by salience band (sal-v6)" table: baseline reached rate of about 4–6% per Term. This matches the frozen cert_anchor of 0.0519.
- CourtListener MCP `search` (type o, court ca11, q `Shaikh "Fox News"`), called twice with different field lists. It found the CA11 opinion in 25-12004 (2026-06-04, published), cluster 10870293.
- CourtListener MCP `read_document` (opinion 11337751): the full per curiam opinion affirming the Rule 12(b)(1) dismissal.
- Two ToolSearch calls to load the MCP tool schemas.
