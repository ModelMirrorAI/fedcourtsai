# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-14.json`, `petition.txt`,
`questions-presented.txt`, `documents.json`, `record/context.json`) and the
committed `metrics/statpack.md`:

- Corpus lookup:
  `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  — stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`.
  Intended as shape context for recent grants; most returned rows were granted
  time-extension applications rather than cert grants, so it informed the
  prediction only marginally.

No CourtListener MCP lookups and no web searches were made. The case's own
disposition was never sought (forward cell; no disposition exists — the
snapshot shows the response due August 24, 2026).
