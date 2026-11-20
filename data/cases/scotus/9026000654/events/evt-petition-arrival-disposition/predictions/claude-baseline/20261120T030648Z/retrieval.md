# Retrieval log

- `uv run fedcourts query --help` — read flags.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — returned only usage/help text (the `--era` value was apparently not accepted); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — 5 recent granted rows (Robinhood Markets v. Sodha; Mullin v. RAICES; Mullin v. Friends of the Ruidosa Church; Goldman Sachs v. Brown; Scanlan v. Coalition for Open Democracy). stderr: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`. General context only; none bears on this question.
- `metrics/statpack.md` — sal-v8 band table (baseline reached rates), amicus-count cut.
- No CourtListener MCP calls and no web searches.
