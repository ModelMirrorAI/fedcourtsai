# Retrieval log — claude-baseline, 20260820T181919Z

Beyond the provisioned inputs (snapshot `2026-06-02.json`, `context.json`,
`documents/petition.txt`, `documents/brief-in-opposition.txt`,
`documents/questions-presented.txt`, `documents.json`) and the committed
`metrics/statpack.md`:

- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  — stderr: `ranged corpus reads: 26 GET(s), 6815744 byte(s)`. Returned five
  recent granted SCOTUS priors (Jouppi, Viramontes, Grant, Grand, Apple v.
  Epic); none CVSG'd, used only as light context on recent grant shapes — the
  statpack's CVSG cut and band table did the anchoring work.

No CourtListener MCP lookups and no web searches were made. I deliberately did
not query this case's own docket or status (the cell is `forward`; nothing
postdating the 2026-06-02 snapshot informed the forecast).
