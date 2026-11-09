# Retrieval

- `uv run fedcourts query --court scotus --docket-number 26-71` — first attempt without `--court` was rejected (usage error naming `--court`); retry returned the row for *The GEO Group v. Ferguson* (CA9 24-2815), distributed for 11/13/2026, distribution_count 3, salience-selected, undecided.
  `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — rejected (unknown era `modern`); retried with `--era 2020s`: returned five recent granted priors (unrelated subject matter; not relied on).
  `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
- Read committed `metrics/statpack.md` (relist-count, CVSG, amicus cuts).
- No CourtListener MCP calls and no web searches.
