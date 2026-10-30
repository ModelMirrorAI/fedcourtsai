# Retrieval

- `uv run fedcourts paths --court scotus --docket 9026000562 --event evt-petition-arrival-disposition --role predictor`: resolved the paths.
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5`: rejected with a usage error (`modern` is not an era token).
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5` printed `ranged corpus reads: 8 GET(s), 2097152 byte(s)`. It returned recent denied petitions, several of them pro se, and served as a general shape check only.
- I read the committed `metrics/statpack.md`, section "Segment base rate by salience band (sal-v4)".
- No CourtListener MCP calls and no web searches.
