# Retrieval log

Beyond the provisioned inputs:

1. `metrics/statpack.md` — relist-count, CVSG-status, amicus-count cuts and the sal-v8 salience band table.
2. `uv run fedcourts query --help` — usage.
3. `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — refused: unknown era `modern` (usage error; no rows).
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5` — 5 rows (recent grants, none on this question; not used). `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
5. `uv run fedcourts query --court scotus --docket-number 26-107` — the Walls v. Prince George's County row (same counsel and amici as the staged related docket). `ranged corpus reads: 17 GET(s), 4456448 byte(s)`

No CourtListener MCP calls and no web searches.
