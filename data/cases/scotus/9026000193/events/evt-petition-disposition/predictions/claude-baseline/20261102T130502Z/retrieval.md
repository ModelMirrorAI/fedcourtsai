# Retrieval

Corpus lookups (beyond the provisioned inputs and `metrics/statpack.md`):

1. `uv run fedcourts query --court scotus --citation "540 U.S. 712" --limit 3`. Returned no rows; it printed a note that the citation column is sparse (200 rows).
   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
2. `uv run fedcourts query --court scotus --citation "596 U.S. 767" --limit 3`. Returned no rows, with the same sparse-column note.
   `ranged corpus reads: 0 GET(s), 0 byte(s)`
3. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`. Usage error: `modern` is not a valid era token. No reads.
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`. Returned 5 recent grants, none of them on this question, so they were not used.
   `ranged corpus reads: 25 GET(s), 6553600 byte(s)`

No CourtListener MCP or web searches were made.
