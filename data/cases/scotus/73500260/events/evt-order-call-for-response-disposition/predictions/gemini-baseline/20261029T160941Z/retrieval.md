# Retrieval Log

## Corpus CLI (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "571 U.S. 69" --limit 5`
   - Transfer: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: 0 rows returned (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: 5 resolved 2020s SCOTUS denied rows returned (`scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9526000555`, `scotus/9526000556`).

3. `uv run fedcourts open-events --stage cert`
   - Transfer: none (CLI usage error: `No such option: --stage`).

4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: 5 resolved 2020s SCOTUS granted rows returned (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`).

5. `uv run fedcourts query --court scotus --decided-before 2026-07-29 --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 25 GET(s), 6356992 byte(s)`
   - Result: 5 SCOTUS granted priors resolved before 2026-07-29 (`scotus/73275187`, `scotus/73275179`, `scotus/73279009`, `scotus/73281006`, `scotus/73500212`).

6. `uv run fedcourts query --court scotus --decided-before 2026-07-29 --disposition denied --limit 5`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from warm cache)
   - Result: 5 SCOTUS denied priors resolved before 2026-07-29 (`scotus/9026005156`, `scotus/9026005158`, `scotus/9026005162`, `scotus/9526000119`, `scotus/9526000121`).

7. `uv run fedcourts open-events --court scotus --docket 73500260`
   - Transfer: none (`open-events` prints no transfer line)
   - Result: `evt-order-call-for-response-disposition`, `evt-petition-disposition`.

## CourtListener MCP

1. `mcp_courtlistener_search` (`type="o"`, `citation="24 F.4th 230"`, `fields=["caseName", "dateFiled", "court_id", "docketNumber", "citation", "cluster_id"]`)
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 6908 seconds.'}`.

2. `mcp_courtlistener_search` (`type="o"`, `case_name="TMX Finance Corporate Services v. Spicher"`, `filed_before="2026-07-29"`, `fields=["caseName", "dateFiled", "court_id", "docketNumber", "citation", "cluster_id"]`)
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 6873 seconds.'}`.

## Web Search

- None attempted.
