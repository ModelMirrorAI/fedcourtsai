# Retrieval log

Beyond the provisioned inputs:

- `metrics/statpack.md` — "The merits docket (granted cases)" and "Per-Justice merits votes (complete lineups)" sections (committed base rates).
- `uv run fedcourts query --help` — read the filter surface.
- `uv run fedcourts query --court scotus --citation "574 U.S. 418"` — empty; stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`, plus the note that only 195 SCOTUS rows carry citations.
- `uv run fedcourts query --court scotus --citation "591 U.S. 549"` — empty; stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`, same coverage note.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — five recent granted rows (applications and petitions unrelated to trademark law); stderr: `ranged corpus reads: 30 GET(s), 7798784 byte(s)`. Not used in the forecast.

No CourtListener MCP calls and no web searches.
