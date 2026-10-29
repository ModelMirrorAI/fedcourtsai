# Retrieval log

Corpus lookups:
- `uv run fedcourts query --court scotus --citation "268 U.S. 510" --limit 5`
  — `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; empty, with a note that
  the citation column is sparse.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
  — usage error (no `--limit`-compatible combination as typed); re-issued below.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  — `ranged corpus reads: 24 GET(s), 6291456 byte(s)`; five recent OT2025/2026
  grants and applications, none on point.

Committed base rates: `metrics/statpack.md` (segment band table sal-v4,
amicus/relist/CVSG cuts, originating circuit).

No CourtListener MCP calls, no web searches, no live-docket fetch.
