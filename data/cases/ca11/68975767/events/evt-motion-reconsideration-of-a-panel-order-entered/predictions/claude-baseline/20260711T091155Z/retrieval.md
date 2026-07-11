# Retrieval log

Beyond the provisioned inputs (event.yaml, snapshot 2026-07-11.json,
record/context.json) I consulted:

## Corpus lookups (`fedcourts`, ranged backend)

- `uv run fedcourts query --court ca11 --topic "3840 Trademark" --limit 8 --corpus-backend ranged`
  → 0 rows. stderr: `ranged corpus reads: 99 GET(s), 25952256 byte(s)`
- `uv run fedcourts query --court ca11 --limit 10 --corpus-backend ranged`
  → 10 rows, all historical `other`/sparse-label ca11 cases, not informative
  for a motion-level reconsideration event. stderr:
  `ranged corpus reads: 45 GET(s), 11796480 byte(s)`

## Base rates

- Read the committed `metrics/statpack.md` (by-court cut: ca11 45 resolved —
  other 95.6%, denied 2.2%, granted 2.2%).

## CourtListener MCP

- None. The cell is `forward` mode with unrestricted retrieval, but the
  provisioned snapshot already contained the event's resolution (disclosed in
  `flags.json`), so I made no CourtListener calls — anything about this case
  risked further outcome exposure, and the pre-decision docket record was
  sufficient for the analysis.

## Web searches

- None.
