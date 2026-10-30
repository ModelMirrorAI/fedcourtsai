# Retrieval Log

## Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr transfer line: `ranged corpus reads: 34 GET(s), 8716288 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS granted cases for baseline comparison.

2. `uv run fedcourts query --court scotus --citation "600 U.S. 122" --limit 5`
   - Stderr transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Empty result with coverage note (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

3. `uv run fedcourts query --court scotus --docket-number 25-1208`
   - Stderr transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned `scotus/73281694` (*Norfolk Southern Railway Company v. Robert Willmore Mallory*, No. 25-1208, cert. denied 2026-10-05 after `distribution_count: 2`).

4. `uv run fedcourts query --court scotus --docket-number 24-1190`
   - Stderr transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72483675` (*Syngenta Crop Protections, LLC, et al. v. Douglas Nemeth, et al.*, No. 24-1190, cert. denied 2025-10-06).

5. `uv run fedcourts query --court scotus --docket-number 21-926`
   - Stderr transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72475093` (*Cooper Tire & Rubber Company v. Tyrance McCall*, No. 21-926, originating from the Supreme Court of Georgia, cert. denied 2023-06-30 after `distribution_count: 4`).

6. `uv run fedcourts query --court scotus --docket-number 21-1168`
   - Stderr transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/65740073` (*Robert Mallory v. Norfolk Southern Railway Co.*, No. 21-1168, cert. granted 2022-04-25, merits decided 2023-06-27 `vacated`).

## CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="Samsung Electronics America Brewer", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "absolute_url"])`
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 2018 seconds.'}`.

2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Mallory v. Norfolk Southern", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "absolute_url"])`
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 2018 seconds.'}`.

## Web Searches

- None attempted.
