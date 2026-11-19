# Retrieval log

- `uv run fedcourts paths --court scotus --docket 9026000648 --event evt-petition-arrival-disposition --role predictor` — resolved cell paths.
- `uv run fedcourts query --help` — read the filter surface.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — returned five recent granted SCOTUS rows (Robinhood Markets v. Sodha; Mullin v. RAICES; Mullin v. Friends of the Ruidosa Church; Goldman Sachs Bank USA v. Brown; Scanlan v. Coalition for Open Democracy). stderr: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`. Not informative on this question; not relied on.
- `metrics/statpack.md` — "Cert petitions by salience band" and "Segment base rate by salience band (sal-v8)" tables (baseline reached rates, prior Terms).
- No CourtListener MCP calls and no web searches.
