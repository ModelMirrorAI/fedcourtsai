# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Result: Returned 10 recent resolved SCOTUS 2020s rows for context on recent dispositions and salience scores.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
   - Result: Returned 10 recent granted SCOTUS 2020s rows (cert petitions and applications) for comparison of distribution counts, counsel representation, and salience profiles.

## CourtListener MCP and Web Retrieval

- None needed beyond the provisioned inputs (`record/snapshots/2026-11-08.json`, `record/context.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, and `record/documents/appendix.txt`), as the appendix reproduces the Fifth Circuit opinion, rehearing denial, and district court orders in full.
