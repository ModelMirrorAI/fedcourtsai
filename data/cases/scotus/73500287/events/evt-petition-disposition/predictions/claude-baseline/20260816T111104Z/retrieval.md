# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `record/documents/petition.txt`,
`record/documents/questions-presented.txt`, `record/documents/documents.json`)
and the committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
   - Purpose: recent granted-petition priors for shape; surfaced *Apple Inc.
     v. Epic Games, Inc.* (25-1311, granted 2026-06-30) as antitrust-docket
     context.

## CourtListener MCP lookups

None.

## Web searches

None.
