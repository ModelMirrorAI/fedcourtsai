# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. **Target docket lookup (`26-171`):**
   - Command: `uv run fedcourts query --court scotus --docket-number 26-171`
   - Transfer line: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned 1 open row (`scotus/9026000171`, `Galesburg Community Unit School District No. 205 v. N. T., Individually and as Parent and Next Friend of C. T., et al.`), showing `distribution_count: 1`, `distributed_for_conference: "2026-10-09"`, `disposition: null`, `salience_score: 0.0182`, `salience_version: "sal-v4"`, and amicus appearance by `National School Attorneys Association, AASA the School Superintendents Association, Association of School Business Officials International, Council of Administrators of Special Educationof`.

2. **Recent 2020s SCOTUS resolved priors:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: Returned 10 recently resolved SCOTUS rows from October 2026 (`scotus/9026000002`, `scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9026000346`, `scotus/9026005347`, `scotus/9526000512`, `scotus/9526000555`, `scotus/9526000556`, `scotus/9526000416`).

3. **Recent 2020s SCOTUS granted priors:**
   - Command: `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 23 GET(s), 5832704 byte(s)`
   - Result: Returned 10 granted SCOTUS rows (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`), providing distribution-count and salience-score context for recent OT 2026 cert grants.

4. **Known IDEA precedent citation lookup:**
   - Command: `uv run fedcourts query --court scotus --citation "598 U.S. 142" --citation "580 U.S. 386" --citation "458 U.S. 176" --limit 10`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: 0 rows returned (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

## 2. CourtListener MCP Calls

1. **`mcp_courtlistener_search` (Opinion search for lower-court opinion):**
   - Args: `{"type": "o", "q": ""Galesburg Community Unit School District"", "fields": ["caseName", "citation", "court", "dateFiled", "docketNumber", "id"]}`
   - Result: Error — `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 5896 seconds.'}`

2. **`mcp_courtlistener_search` (Opinion search for IDEA `1415(i)(2)(C)` / `Rowley` due-weight precedent):**
   - Args: `{"type": "o", "q": ""Rowley" "due weight" "additional evidence" "1415(i)(2)(C)"", "fields": ["caseName", "citation", "court", "dateFiled", "docketNumber", "id"]}`
   - Result: Error — `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 5896 seconds.'}`

## 3. Web Searches

None attempted.
