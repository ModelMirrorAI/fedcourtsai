# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/petition.txt`, `record/documents/questions-presented.txt`, `record/documents/documents.json`), the event definition, `schemas/prediction.schema.json`, and the committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   Returned five granted 2020s SCOTUS rows (four substantive applications with government or state parties and amici; one counseled cert petition, Jouppi v. Alaska). None resembled a pro se conspiracy petition; used only as a negative check, described in `reasoning.md`.

## CourtListener MCP lookups

None.

## Web searches

None.
