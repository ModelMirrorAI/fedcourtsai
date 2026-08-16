# Retrieval

- Consulted `metrics/statpack.md`, “The merits docket (granted cases),” for the strictly prior grant-Term disturbed-rate anchor and its parsed-coverage and exclusion counts.
- CourtListener MCP opinion search for citation `999 F.3d 190` (*Obando-Segura*): HTTP 429 rate-limit error; no result used.
- CourtListener MCP opinion search for citation `169 F.4th 418` (*Michelin*): HTTP 429 rate-limit error; no result used.
- CourtListener MCP opinion search for citation `158 F.4th 1152` (*Daley*): HTTP 429 rate-limit error; no result used.
- `uv run fedcourts query --court scotus --citation '553 U.S. 571' --limit 1 --full` (*Richlin*): attempted twice; no result or `ranged corpus reads` line was returned before timeout.
- `uv run fedcourts query --court scotus --citation '541 U.S. 401' --limit 1 --full` (*Scarborough*): no result or `ranged corpus reads` line was returned before timeout.
- `uv run fedcourts query --court scotus --citation '566 U.S. 284' --limit 1 --full` (*Cooper*): no result or `ranged corpus reads` line was returned before timeout.

No web search was used.
