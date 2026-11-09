# Retrieval Log

Beyond the provisioned inputs under `data/cases/scotus/73280982/record/` and `metrics/statpack.md`, the following CLI and corpus lookups were executed:

1. **Path resolution (`fedcourts paths`)**:
   - Command: `uv run fedcourts paths --court "scotus" --docket "73280982" --event "evt-order-relist-disposition" --role predictor`
   - Result: Resolved `case_id` (`scotus/73280982`), `corpus` (`corpus/corpus.db`), and `event` path (`data/cases/scotus/73280982/events/evt-order-relist-disposition/event.yaml`).

2. **Query CLI help (`fedcourts query --help`)**:
   - Command: `uv run fedcourts query --help`
   - Result: Inspected available structured filters for `fedcourts query`.

3. **Corpus query by reporter citations (`fedcourts query`)**:
   - Command: `uv run fedcourts query --court scotus --citation "601 U.S. 257" --citation "575 U.S. 175" --citation "604 U.S. 4" --citation "604 U.S. 20" --limit 10`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (printed coverage note that only 200 SCOTUS rows in the corpus table carry parallel reporter citations).

4. **Corpus query for recent granted SCOTUS petitions (`fedcourts query`)**:
   - Command: `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Result: Returned 10 recent granted SCOTUS cases in the 2020s era (including recent OT2025/OT2026 cert grants such as `scotus/73520108`, `scotus/9026000012`, `scotus/9026000204`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, and `scotus/73281619`), showing typical `distribution_count` values (2 to 5) on relisted petitions granted in October and November 2026.

No CourtListener MCP calls or external web searches were made.
