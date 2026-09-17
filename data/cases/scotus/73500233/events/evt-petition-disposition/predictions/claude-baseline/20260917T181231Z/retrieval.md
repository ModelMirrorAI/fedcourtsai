# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-09-17.json`,
`record/context.json`, `record/documents/petition.txt`,
`record/documents/questions-presented.txt`, `record/documents/documents.json`)
and the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --limit 8 --era 2020s`
  stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
  Returned eight recent SCOTUS rows, all interim applications or recently
  denied petitions unrelated to this case's issue; none used in the forecast.

## CourtListener MCP lookups

- `search` (type `d`, court `scotus`, docket_number `25-1333`): refused with
  HTTP 429 (rate limit exceeded, 300/hour, retry advised in about three
  minutes). Not retried; the provisioned snapshot is dated today.

## Web searches

None.
