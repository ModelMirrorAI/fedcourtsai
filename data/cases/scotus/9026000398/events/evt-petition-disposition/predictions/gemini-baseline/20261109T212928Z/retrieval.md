# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-459`
   - Stderr transfer line: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Result: 1 row returned (`scotus/73278510`, *Michael Salazar v. Paramount Global, dba 247Sports*, No. 25-459, originating from CA6 No. 23-5748, cert granted 2026-01-26).
2. `uv run fedcourts query --court scotus --docket-number 24-994`
   - Stderr transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: 1 row returned (`scotus/72487279`, *National Basketball Association v. Michael Salazar*, No. 24-994, originating from CA2 No. 23-1147, cert denied 2025-12-08).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr transfer line: `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
   - Result: 10 recent granted SCOTUS rows returned from the 2020s era.
4. `uv run fedcourts query --court scotus --citation "146 S. Ct. 885" --citation "146 S. Ct. 1790"`
   - Stderr transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: 0 rows returned (printed coverage note that only 200 rows in scope carry reporter citations).
5. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Stderr transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: 10 recent denied SCOTUS rows returned from the 2020s era.

## CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Solomon v. Flipps Media", fields=["caseName", "docketNumber", "dateFiled", "citation", "docket_id", "cluster_id"])`
   - Result: `count: 0`, `results: []`.
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Hughes v. National Football League", fields=["caseName", "docketNumber", "dateFiled", "citation", "docket_id", "cluster_id"])`
   - Result: `count: 0`, `results: []`.
3. `mcp_courtlistener_search(type="r", case_name="Solomon v. Flipps Media", fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id"])`
   - Result: `count: 2` (CA2 No. 23-7597, `docket_id: 69423528`; E.D.N.Y. No. 2:22-cv-05508, `docket_id: 65349479`).
4. `mcp_courtlistener_search(type="r", case_name="Salazar v. Paramount", fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id"])`
   - Result: `count: 2` (CA6 No. 23-5748, `docket_id: 67928839`; M.D. Tenn. No. 3:22-cv-00756, `docket_id: 65385135`).
5. `mcp_courtlistener_search(type="o", court="scotus", q=""Flipps Media" OR "Hughes v. National Football League" OR "Salazar v. Paramount"", fields=["caseName", "docketNumber", "dateFiled", "citation", "docket_id", "cluster_id"])`
   - Result: `count: 0`, `results: []`.
6. `mcp_courtlistener_search(type="oa", court="scotus", q="Salazar v. Paramount", fields=["caseName", "docketNumber", "dateArgued", "docket_id"])`
   - Result: `count: 1` (*Salazar v. Paramount Global*, No. 25-459, `docket_id: 73278510`, argued `2026-10-14`).
7. `mcp_courtlistener_search(type="o", case_name="Solomon v. Flipps Media", fields=["caseName", "docketNumber", "dateFiled", "citation", "docket_id", "cluster_id", "opinions"])`
   - Result: `count: 1` (*Detrina Solomon v. Flipps Media, Inc.*, 136 F.4th 41, CA2 No. 23-7597, decided `2025-05-01`, `cluster_id: 10439012`, `opinion_id: 10905600`).
8. `mcp_courtlistener_search(type="o", case_name="Salazar v. Paramount Global", fields=["caseName", "docketNumber", "dateFiled", "citation", "docket_id", "cluster_id", "opinions"])`
   - Result: `count: 1` (*Michael Salazar v. Paramount Global*, 133 F.4th 642, CA6 No. 23-5748, decided `2025-04-03`, `cluster_id: 10372262`, `opinion_id: 10838850`).

## Web Searches

- None attempted.
