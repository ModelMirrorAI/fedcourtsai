# Retrieval log

Beyond the provisioned record (snapshot, QP, petition, documents.json) and the committed `metrics/statpack.md`:

1. `uv run fedcourts query --court scotus --citation "523 U.S. 833" --limit 5`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - No rows. A `note:` line said the citation column is sparse (200 SCOTUS rows carry any citation).
2. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
   - Usage error (flag combination not accepted as given). Help text printed. No reads reported.
3. `uv run fedcourts query --court scotus --disposition granted --limit 5`
   - `ranged corpus reads: 24 GET(s), 6291456 byte(s)`
   - Returned recent OT2025/26 grants (mostly federal-government petitions and applications). None was substantively comparable, so they were used only to confirm the shape of the population.

No CourtListener MCP calls and no web searches.
