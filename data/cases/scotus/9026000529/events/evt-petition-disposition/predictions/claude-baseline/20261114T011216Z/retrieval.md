# Retrieval log

- Read committed `metrics/statpack.md` (relist-count cut, salience-band cut, per-Term "Segment base rate by salience band (sal-v8)" table; grep for a CAAF/armed-forces originating-court row found none).
- `uv run fedcourts query --help` — read the interface.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (`modern` is not an era token); no rows.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5` — `ranged corpus reads: 8 GET(s), 2031616 byte(s)`; 5 generic recent denials (Pavatt v. Oklahoma, Schultz v. Gold, Schultz v. McCarthy, Jesenik v. United States); not specific to this case's posture.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3` — `ranged corpus reads: 18 GET(s), 4718592 byte(s)`; 3 generic recent grants (Mullin v. Friends of ..., Goldman Sachs Bank USA v. ...); not used beyond context.
- No CourtListener MCP calls and no web searches.
