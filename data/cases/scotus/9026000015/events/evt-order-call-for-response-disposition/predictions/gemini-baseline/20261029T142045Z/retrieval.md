# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
   - Result: Returned 10 recent granted SCOTUS petitions/applications from the 2020s era (including `scotus/73281619`, *Missionaries of Saint John the Baptist, Inc. v. Joel Frederic, et ux.*).
2. `uv run fedcourts query --court scotus --docket-number 23-1226 --limit 5`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned 1 row (`scotus/69562299`, *McLaughlin Chiropractic Associates, Inc. v. McKesson Corporation, et al.*).
3. `uv run fedcourts query --court ca5 --judge Stewart --judge Richman --judge Higginson --limit 10`
   - Transfer: `ranged corpus reads: 116 GET(s), 30408704 byte(s)`
   - Result: Returned 0 rows (circuit judge lists are withheld in the corpus slice).
4. `uv run fedcourts query --court scotus --citation "593 U.S. 522" --citation "595 U.S. 411" --limit 10`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned 0 rows with note on sparse reporter-citation coverage.
5. `uv run fedcourts query --court scotus --docket-number 24-97`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned 1 row (`scotus/72487253`, *Mark Randall Meadows v. Georgia*).
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Result: Returned 10 recent denied SCOTUS rows from the 2020s era.
7. `uv run fedcourts query --court scotus --docket-number 24-91`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/72487188`, *Targeted Justice, Inc. v. Garland*).
8. `uv run fedcourts query --court scotus --docket-number 24-291`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/70377102`, *Apache Stronghold v. United States, et al.*, denied 2025-05-27 after 18 distributions, salience score 0.4108).
9. `uv run fedcourts query --court scotus --docket-number 23A824`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/72415325`, *Vance v. Engstrom*).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(case_name="Perez v. City of San Antonio", court="ca5", type="o", fields=["caseName", "dateFiled", "citation", "docketNumber", "judge", "cluster_id"])`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 1079 seconds.`). Degraded gracefully and relied on the lower-court opinions reproduced in the provisioned petition and appendix.

## 3. Web Searches

None attempted.
