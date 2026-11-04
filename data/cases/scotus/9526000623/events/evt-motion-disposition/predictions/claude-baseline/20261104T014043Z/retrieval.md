# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 8` → usage error (`modern` is not an era token, and `--docket-number` needs `--court`). No rows.
- `uv run fedcourts query --docket-number 26-6013` → usage error (needs `--court`).
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --include-applications --limit 8`
  - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
  - Returned recent denied substantive applications (mostly non-capital, pro se). Shape only.
- `uv run fedcourts query --court scotus --docket-number 26-6013 --include-open`
  - `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
  - The linked cert petition: Guardado v. Florida, capital, filed 2026-10-30, 0 distributions, undecided.
- Read `metrics/statpack.md` (interim section) and `metrics/statpack.json` (`interim.terms[]` finer counts).
- No CourtListener MCP or web calls.
