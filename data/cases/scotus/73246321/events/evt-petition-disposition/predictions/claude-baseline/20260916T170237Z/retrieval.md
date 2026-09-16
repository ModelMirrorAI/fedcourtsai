# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-16.json`, `context.json`,
`documents/petition.txt`, `documents/questions-presented.txt`,
`documents.json`, `event.yaml`) and the committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   — returned recent denied SCOTUS rows ranked by recency (August–September
   2026 denials, several of them substantive applications); none specific to
   this case or its questions. Used only to confirm the shape of the recent
   denied population.
   stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`

## CourtListener MCP lookups

None.

## Web searches

None.
