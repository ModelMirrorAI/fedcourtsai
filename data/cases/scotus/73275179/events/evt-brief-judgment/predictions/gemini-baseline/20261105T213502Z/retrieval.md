# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - Transfer: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
   - Result: Returned 5 recent 2020s granted SCOTUS rows (`26A512`, `26-12`, `26-204`, `26A476`, `25-1103`).

2. `uv run fedcourts query --court scotus --citation "597 U.S. 1" --citation "602 U.S. 680" --limit 5`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: 0 rows returned (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

## CourtListener MCP & Web Search

- No CourtListener MCP calls or open-web searches were needed beyond the provisioned case documents (`petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, `merits-brief-petitioner.txt`, `merits-brief-respondent.txt`, `merits-amicus-united-states.txt`, and `questions-presented.txt`), the provisioned snapshots (`2026-10-22.json` and `related/25-566.json`), and `metrics/statpack.md`.
