# Retrieval log

- **Corpus:** `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
  printed usage/help text instead of rows (I did not identify which flag it refused). Re-issued without `--era`.
- **Corpus:** `uv run fedcourts query --court scotus --disposition granted --limit 5`
  printed `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. It returned five recent
  granted SCOTUS rows, none on point, so I used it only as context.
- **Committed statpack:** read `metrics/statpack.md` for the sal-v4 band table, the
  amicus, relist and CVSG cuts, and the circuit cuts.
- **Web:** WebFetch of the Court's live docket page for No. 26-15
  (supremecourt.gov). It shows twelve amicus briefs filed Aug 3–31, 2026, and the
  respondent's time to respond extended twice, to Oct 30, 2026. The petition
  has no disposition yet.
- No CourtListener MCP calls.
