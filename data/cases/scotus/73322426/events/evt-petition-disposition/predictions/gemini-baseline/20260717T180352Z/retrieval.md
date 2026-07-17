# Retrieval Log

- **CourtListener MCP `search`**: Queried `courtlistener_search` for opinions with `q="two-way video" AND "confrontation clause" AND ("Craig" OR "Crawford")` which revealed numerous recent state supreme court and federal appellate decisions addressing this split, confirming it is an active, widespread issue.
- **Corpus Tooling (Attempted)**: Attempted to run `uv run fedcourts query --court scotus --citation "541 U.S. 36" --citation "497 U.S. 836"` to search for SCOTUS precedents in the corpus.
- **Base Rates**: Consulted the committed `metrics/statpack.md` to evaluate base rates for modern discretionary-cert petitions and the impact of the originating court and response signals.
