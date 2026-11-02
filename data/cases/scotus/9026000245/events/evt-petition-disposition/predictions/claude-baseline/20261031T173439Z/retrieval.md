# Retrieval

- `uv run fedcourts query --court scotus --docket-number 23-9` (the first try, without `--court`, was rejected with a usage error) → the corpus row for the prior petition AstraZeneca v. Atchley (No. 23-9), with SG Prelogar listed as counsel. `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` → rejected (unknown era token); not retried.
- `uv run fedcourts query --court scotus --docket-number 25-1323 --include-open` → unrelated row (City of Bossier City v. Hershey); I sent it only to check the flag syntax. `ranged corpus reads: 1 GET(s), 262144 byte(s)`
- Read `metrics/statpack.md` (relist, CVSG and amicus cuts; the sal-v6 band table).
- No CourtListener MCP calls and no web searches.
