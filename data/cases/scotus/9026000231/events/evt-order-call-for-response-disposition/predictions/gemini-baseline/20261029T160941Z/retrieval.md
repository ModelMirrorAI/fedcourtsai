# Retrieval Log

## 1. Local Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000231" --event "evt-order-call-for-response-disposition" --role predictor`
   - Output: resolved `case_id` (`scotus/9026000231`), `corpus` (`corpus/corpus.db`), and `event` path.

2. `uv run fedcourts query --help`
   - Output: CLI help text for `fedcourts query`.

3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 31 GET(s), 7929856 byte(s)`
   - Output: 10 recent OT 2026 granted SCOTUS rows (e.g., `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, `26-104`).

4. `uv run fedcourts query --court scotus --docket-number 25-7193`
   - Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Output: `scotus/73284452`, *Jesus Ramiro Gomez v. United States*, docket `25-7193` (from CA9 `23-435`), cert denied `2026-05-18`.

5. `uv run fedcourts query --court scotus --citation "593 U.S. 420" --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Output: 0 rows (note on citation filter coverage).

6. `uv run fedcourts query --court scotus --citation "604 U.S. 423" --limit 10`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Output: 0 rows (note on citation filter coverage).

7. `uv run fedcourts query --court scotus --docket-number 26-231`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Output: `scotus/9026000231`, *Mario Delaine v. United States*, `disposition: null` (unresolved), listing counsel (`Lisa S. Blatt`, `D. John Sauer`, `Adeel Mohammad Bashir` for NACDL) and `salience_score: 0.0235`.

8. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Output: 5 recent OT 2026 denied SCOTUS rows.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="ca6", case_name="Delaine", fields=["caseName", "dateFiled", "docketNumber", "citation", "judge", "cluster_id", "opinions"])`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 7474 seconds.`).

2. `mcp_courtlistener_search(type="o", court="ca11", case_name="Sheely", fields=["caseName", "dateFiled", "docketNumber", "citation", "judge", "cluster_id"])`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 7474 seconds.`).

3. `mcp_courtlistener_search(type="o", court="ca9", case_name="Lopez", filed_after="2026-07-01", fields=["caseName", "dateFiled", "docketNumber", "citation", "judge", "cluster_id"])`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 7474 seconds.`).

## 3. Web Searches

None attempted.
