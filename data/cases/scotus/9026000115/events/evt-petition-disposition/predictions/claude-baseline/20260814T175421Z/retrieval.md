# Retrieval log

Beyond the provisioned inputs (snapshot, `event.yaml`, `record/context.json`,
`record/documents/petition.txt` and `questions-presented.txt`) and the
committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  - stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
  - Returned recent resolved SCOTUS rows (mostly capital-case denials and
    granted extension applications); no close subject-matter comparables — the
    SCOTUS rows carry no topic filter. Used only as a shape check on the
    recent docket.

## CourtListener MCP lookups

- `search` (type `o`, court `ca4`, q `Dodson "Lutheran Village"`) — 0 results.
- `search` (type `o`, court `ca4`, docket_number `25-1696`) — 0 results.
  - Together these confirm the Fourth Circuit's decision is not indexed as an
    opinion on CourtListener, consistent with the petition's statement that it
    is unreported. Neither query touched this case's SCOTUS docket or
    disposition (forward cell; the petition is pending).

## Web searches

None.
