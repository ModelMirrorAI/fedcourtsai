# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 8`
  → usage error (`--era` takes decade values such as `2020s`); re-issued below.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --include-applications --limit 8`
  → `ranged corpus reads: 7 GET(s), 1835008 byte(s)`. Returned recent denied applications, mostly pro se (e.g., Walker v. Purdue, Lancranjan v. Truitt, Cooper v. Swern).
- `uv run fedcourts query --court scotus --docket-number 26A612` (run twice, the second time to read the disposition fields)
  → `ranged corpus reads: 11 GET(s), 2883584 byte(s)` on the first run (stderr suppressed on the second). Pending: disposition null, no response requested, not referred.
- `uv run fedcourts query --help` (usage only).
- CourtListener MCP `search` with a `query` argument → invalid-argument error. Re-issued as
  `search(type=d, q='Akerman "Merit Systems Protection Board"')` → 19 dockets, including Akerman's suits in D.D.C., E.D. Va. and D. Nev.
- Read `metrics/statpack.md` (interim section) and `metrics/statpack.json` (`interim.terms` finer counts).
