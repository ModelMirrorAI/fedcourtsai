# Retrieval log

- `uv run fedcourts query --help` — read the flag list.
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — refused: `Unknown era 'modern'` (usage error, no rows). Issued twice (the first time with output truncated).
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — returned 5 recent granted rows (e.g. Robinhood Markets v. Sodha; Goldman Sachs Bank USA v. Brown; several federal-petitioner matters). stderr: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`. Not on point; did not move the forecast.
- `metrics/statpack.md` — read the salience-band table (sal-v8), the segment base rate by band per Term, and the relist-count cut (paid scored segment).
- No CourtListener MCP calls and no web searches.
