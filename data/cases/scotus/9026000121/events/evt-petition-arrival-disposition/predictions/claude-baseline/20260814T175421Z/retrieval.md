# Retrieval log — claude-baseline, run 20260814T175421Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-14.json`,
`record/context.json`, `record/documents/questions-presented.txt`,
`record/documents/petition.txt`, `record/documents/documents.json`) and the
committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 5`
  - stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
  - Returned 5 recent resolved SCOTUS priors (recency-ranked; mostly capital
    dockets, not topically similar). Used only to sanity-check row shape and
    confirm the query surface has no free-text/topical filter for SCOTUS rows
    that could retrieve Caperton-adjacent recusal petitions — so base-rate
    anchoring came from the committed statpack instead. No prior's outcome fed
    the number directly, and this case's own docket was not queried.

## CourtListener MCP

None.

## Web searches

None.
