# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25A1239`
   - Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned `scotus/9525001239` (*Darcy Roake, et al. v. Cade Brumley, et al.*, `25A1239`), confirming the granted extension application filed May 11, 2026 and decided May 13, 2026 from Fifth Circuit docket `24-30706`.

2. `uv run fedcourts query --court scotus --include-open --limit 30`
   - Stderr: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Result: Returned 30 recent SCOTUS corpus rows to inspect recent OT2025/OT2026 docketed petitions and applications.

3. `uv run fedcourts query --court scotus --judge "James C. Ho" --include-open --limit 20`
   - Stderr: `ranged corpus reads: 640 GET(s), 167772160 byte(s)`
   - Result: Returned 0 rows (live-channel SCOTUS rows do not populate the `judges` list).

4. `uv run fedcourts query --court scotus --docket-number 25-1360`
   - Stderr: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: Returned the corpus metadata row for `scotus/73500261` (`25-1360`).

## CourtListener MCP Lookups

None.

## Web Searches

None.
