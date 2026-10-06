# Retrieval log

Provisioned inputs read: `record/snapshots/2026-10-05.json`,
`record/context.json`, `record/documents/documents.json`,
`record/documents/questions-presented.txt`, `record/documents/petition.txt`,
`record/documents/brief-in-opposition.txt`, the event's `event.yaml`, and
the committed `metrics/statpack.md`.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 27 GET(s), 6946816 byte(s)`
  Returned eight recent OT2026 grants (25-1131, 25-1349, 26-104, 26A428,
  26-426, 26A406, 26A308, 26A388). None concerns military commissions or
  mandamus; used only as a sanity check on how the corpus records
  distributions and grants.

## CourtListener MCP lookups

- `search(type=d, court=scotus, docket_number="26-13")` — 0 results.
- `search(type=d, court=scotus, case_name="Mohammad v. United States", filed_after=2026-06-01)` — 0 results.
  Both were attempts to read the companion petition's distribution
  schedule. Not found; the companion's state is inferred from the BIO's
  footnote 1 and the reschedule pattern only.

## Web searches

None.

No lookup touched this case's own disposition or post-snapshot docket state.
