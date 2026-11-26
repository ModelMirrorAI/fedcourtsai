# Retrieval log

Beyond the provisioned inputs:

1. `uv run fedcourts query --help` and `uv run fedcourts paths --court scotus --docket 9026000279 --event evt-petition-disposition --role predictor` — usage and path resolution only.
2. `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 8` — rejected: `Unknown era 'modern'` (usage error; no rows, no transfer line).
3. `uv run fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 8` — returned no rows. stderr: `ranged corpus reads: 1146 GET(s), 300220416 byte(s)`.
4. `uv run fedcourts query --court scotus --docket-number 25-690` — one row, Thornell v. Bieganski (cited in the petition as a decision reading Andrew v. White): denied 2026-04-20 after two distributions. stderr: `ranged corpus reads: 19 GET(s), 4980736 byte(s)`.
5. `metrics/statpack.md` — modern cert dispositions, relist / CVSG / amicus / capital cuts, per-Term table, and the salience band table (headed sal-v8).

No CourtListener MCP calls and no web searches were made.
