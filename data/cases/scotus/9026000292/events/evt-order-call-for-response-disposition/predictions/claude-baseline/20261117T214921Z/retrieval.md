# Retrieval log

- `uv run fedcourts query --help` (flag listing; no corpus read).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — returned only usage text (no rows); re-issued without `--era`.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 33 GET(s), 8650752 byte(s)`; five recent granted SCOTUS rows (Robinhood Markets v. Sodha; Mullin v. RAICES; Mullin v. Friends of the Ruidosa Church; Goldman Sachs Bank USA v. Brown; Scanlan v. Coalition for Open Democracy). None related to this case; not used.
- Committed `metrics/statpack.md`: relist-count, CVSG-status, amicus-count and salience-band cuts, and the sal-v8 per-Term band table.
- No CourtListener MCP calls and no web searches.
