# Retrieval log

- `uv run fedcourts query --docket-number 25-107` → usage error (needs `--court`); printed the help text.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` → `ranged corpus reads: 29 GET(s), 7602176 byte(s)`; recent granted petitions, used only as general shape.
- `uv run fedcourts query --court scotus --docket-number 25-107` → `ranged corpus reads: 11 GET(s), 2883584 byte(s)`; Gilliam v. Gerregano, denied 2025-12-08, distribution_count 2, no CVSG, amici including FIRE, Volokh/Tam, ACLJ, WILL/Buckeye, Protect the First.
- Read `metrics/statpack.md` (salience band table, sal-v6).
- No CourtListener MCP or web searches.
