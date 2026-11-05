# Retrieval log

Beyond the provisioned inputs (snapshot 2026-11-04.json, context.json, documents/, argument-features.json) and the committed `metrics/statpack.md`:

1. `uv run fedcourts paths --court scotus --docket 73279026 --event evt-argument-judgment --role predictor` — path listing only.
2. `uv run fedcourts query --court scotus --citation "596 U.S. 767" --citation "593 U.S. 522" --citation "591 U.S. 464" --limit 5`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. No rows came back; a `note:` said the citation column is sparse (200 SCOTUS rows).
3. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`. Usage error ("modern" is not a valid era); no read.
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. Returned recent unrelated grants (e.g., Scanlan v. Coalition for Open Democracy, DOJ v. McNutt). None was used.

No CourtListener MCP calls. No web searches.
