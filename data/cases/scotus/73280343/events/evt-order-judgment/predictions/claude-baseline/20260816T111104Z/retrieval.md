# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `event.yaml`, and the provisioned documents
`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt` — the
last with `empty_text: true`):

- Committed base rates: read `metrics/statpack.md`, "The merits docket
  (granted cases)" section (the registered merits baseline feed).
- Corpus lookup (one call):
  - `uv run fedcourts query --court scotus --citation "742 F.3d 603"`
    — stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`; returned
    no rows, with the printed `note:` naming the citation column's coverage
    gap (161 of 590,339 SCOTUS-scope rows carry citation data, own-cites
    only).
- CourtListener MCP: not used.
- Web searches: none.
