# Retrieval log

Beyond the provisioned inputs (snapshot, context.json, event.yaml, record/documents/*) and the committed `metrics/statpack.md`:

1. `uv run fedcourts paths --court scotus --docket 73280982 --event evt-order-judgment --role predictor` — resolved case, corpus and event paths.
2. `uv run fedcourts query --help` — read the interface.
3. `uv run fedcourts query --court scotus --citation "601 U.S. 257" --citation "575 U.S. 175"` — `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; no rows, with the note that only 195 SCOTUS rows carry a reporter citation (coverage gap, not absence).
4. `uv run fedcourts query --court scotus --disposition reversed --era modern` — refused: unknown disposition `reversed`. No transfer line.
5. `uv run fedcourts query --court scotus --disposition granted --era modern` — refused: unknown era `modern`. No transfer line.
6. `uv run fedcourts query --court scotus --disposition granted --era 2020s` — `ranged corpus reads: 40 GET(s), 10420224 byte(s)`; returned recent granted dockets (this case's own row first, then unrelated grants and applications). Not subject-matched; not used in the forecast.

No CourtListener MCP calls. No web searches. No merits briefs or argument material retrieved.
