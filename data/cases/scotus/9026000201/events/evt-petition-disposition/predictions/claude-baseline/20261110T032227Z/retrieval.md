# Retrieval log

- `uv run fedcourts query --docket-number 25-1325 2>&1` → usage error (needs `--court`); no rows.
- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` → usage error (unknown era); no rows.
- `uv run fedcourts query --court scotus --docket-number 25-1325 --include-open`
  `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. Returned Oklahoma v. United States: pending, distributed 2026-10-09, distribution_count 1, SG and HISA as respondents.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Returned generic recent grants (shape only, not used substantively).
- Read `metrics/statpack.md` (salience band table, relist-count cut).
- No CourtListener MCP calls and no web searches.
