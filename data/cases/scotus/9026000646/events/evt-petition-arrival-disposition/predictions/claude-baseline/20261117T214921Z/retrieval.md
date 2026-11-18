# Retrieval log

- `uv run fedcourts paths --court scotus --docket 9026000646 --event evt-petition-arrival-disposition --role predictor` — resolved paths.
- `uv run fedcourts query --help` — read the flag vocabulary.
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — rejected (usage error: `modern` is not an era token).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` — returned granted priors (first row: Robinhood Markets, Inc. v. Sodha). stderr: `ranged corpus reads: 36 GET(s), 9437184 byte(s)`.
- Read `metrics/statpack.md` (salience-band table, segment base rate by band, originating-court cut).
- No CourtListener MCP calls and no web searches.
