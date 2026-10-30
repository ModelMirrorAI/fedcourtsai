# Retrieval Log (`retrieval.md`)

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-433`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned 1 row (`scotus/9026000433`, *Karen Brookins, Individually and as Administratrix of the Estate of Marcus Richard Boone v. City of Philadelphia, Pennsylvania, et al.*, `salience_score: 0.024`, `distribution_count: 1`, `originating_court: "ca3"`).

2. `uv run fedcourts query --court scotus --limit 5`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Result: Returned 5 recent OT 2026 resolved SCOTUS rows (`scotus/9026000002`, `scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9026000346`).

3. `uv run fedcourts query --court scotus --topic constitutional-rights --limit 10`
   - Transfer: None (`corpus service at http://127.0.0.1:8377 timed out after 180s — a slow corpus read, not a dead sidecar: ReadTimeout('timed out')`).
   - Result: Timed out (`--topic` is an exact nature-of-suit filter on circuit rows only).

## CourtListener MCP Calls

- None (`0` calls).

## Web Searches

- None (`0` calls).
