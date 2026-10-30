# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Stderr transfer line: `ranged corpus reads: 34 GET(s), 8716288 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS GVR priors (including OT 2026 Long Conference GVRs in `scotus/73317900`, `scotus/73500268`, `scotus/9026000139`, `scotus/73280412`, `scotus/73280426`, and `scotus/9026000048`), showing distribution counts (typically 1–3) and salience scores.

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS granted priors from the warm service cache.

3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS denied priors from the warm service cache.

4. `uv run fedcourts query --court ca9 --citation "156 F.4th 979" --limit 5`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 0 rows with coverage note that the `ca9` slice carries no populated reporter citations in that column.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="ca9", case_name="King v. Villegas", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions", "status"])`
   - Result: Failed with HTTP 429 rate-limit error (`Request was throttled. Rate limit exceeded: 1400/day. Expected available in 8884 seconds.`).

2. `mcp_courtlistener_search(type="o", court="ca9", case_name="Cardenas v. City of Santa Maria", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions", "status"])`
   - Result: Failed with HTTP 429 rate-limit error (`Request was throttled. Rate limit exceeded: 1400/day. Expected available in 8884 seconds.`).

## 3. Web Searches (`google_web_search`)

1. `google_web_search(query='"King v. Villegas" "23-1713" "en banc"')`
   - Result: Confirmed that the Ninth Circuit granted rehearing en banc and vacated the panel opinion on April 3, 2026 (*King v. Villegas*, 171 F.4th 1163), heard en banc oral argument on June 2, 2026, and that the en banc decision in *King v. Villegas* (No. 23-1713) remains pending as of late October 2026.
