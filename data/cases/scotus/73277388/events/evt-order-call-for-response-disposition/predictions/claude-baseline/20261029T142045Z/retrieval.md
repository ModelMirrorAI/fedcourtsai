# Retrieval log

- `uv run fedcourts query --help` (usage only).
- `uv run fedcourts query --court scotus --docket-number 25-34` — `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned the companion *Continental Finance Co. v. Johnson* (scotus/73272764): ca4, filed 2025-07-10, disposition `dismissed`, dated 2026-05-07, distribution_count 0.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — `ranged corpus reads: 24 GET(s), 6291456 byte(s)`. Returned recent grants, mostly government parties. Not informative for this case.
- `metrics/statpack.md`, read for base rates (the sal-v4 band table, the amicus cut and the relist/CVSG cuts).
- No CourtListener MCP calls and no web searches.
