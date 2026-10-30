# Retrieval Log

## 1. Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "601 U.S. 330" --limit 5`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Empty (printed note explaining that only 200 rows in `scotus` scope carry reporter citations).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 31 GET(s), 7929856 byte(s)`
   - Result: Returned 10 recent granted SCOTUS priors from the 2020s era (including `scotus/9026000012`, `scotus/9026000204`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`).

3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 5 recent denied SCOTUS rows from the 2020s era (served from warm cache).

4. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 5 recent GVR SCOTUS priors from the 2020s era (`scotus/73317900`, `scotus/73500268`, `scotus/73500579`, `scotus/9026000139`, `scotus/9026005216`, served from warm cache).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", q=""32.2(b)(4)(B)" "McIntosh"", num_results=10, fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "snippet"])`
   - Result: Failed with HTTP 429 rate limit (`Rate limit exceeded: 1400/day. Expected available in 209 seconds.`).

2. `mcp_courtlistener_search(type="o", court="ca6", case_name="Harrell", q=""32.2(b)(4)(B)"", num_results=5, fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "snippet"])`
   - Result: Failed with HTTP 429 rate limit (`Rate limit exceeded: 1400/day. Expected available in 209 seconds.`).

## 3. Web Searches

None attempted.
