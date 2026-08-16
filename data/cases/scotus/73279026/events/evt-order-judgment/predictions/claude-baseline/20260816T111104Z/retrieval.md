# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `event.yaml`, and the provisioned documents
`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt` with
`documents.json`) and the committed `metrics/statpack.md`:

- `uv run fedcourts query --court scotus --citation "593 U.S. 522" --limit 3`
  — timed out after 90s with no output; no `ranged corpus reads:` line was
  printed.
- `uv run fedcourts query --court scotus --citation "593 U.S. 522" --limit 3
  --corpus-backend service` — timed out after 45s with no output; no
  `ranged corpus reads:` line was printed.

No corpus priors were retrieved. No CourtListener MCP calls were made. No web
searches were made.
