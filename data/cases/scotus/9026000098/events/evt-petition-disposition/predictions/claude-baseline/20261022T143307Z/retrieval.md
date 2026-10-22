# Retrieval log

- `uv run fedcourts query --court scotus --text "NVRA public disclosure voter registration list" --limit 5` — failed (no `--text` flag; printed help). No `ranged corpus reads` line.
- Read committed `metrics/statpack.md` (sal-v4 band table, relist and CVSG cuts, circuit cut).
- CourtListener MCP `search` (type o): `"20507(i)" voter registration list Benson`, filed after 2026-01-01 — surfaced CA9 *PILF v. Nago* (the decision below), CA7 *PILF v. Wolfe*, CA4 *PILF v. Wooten*, CA8 *PILF v. Simon*, CA6 *United States v. Benson*, D.D.C. *US v. Evans*, *Common Cause v. DOJ*.
- CourtListener MCP `search` with multi-court filter — validation error (no result).
- CourtListener MCP `search` (type o): `"20507(i)" "statewide" list record`, filed after 2026-07-01 — case names/snippets only; no opinions read in full.

Nothing surfaced about this petition's own disposition.
