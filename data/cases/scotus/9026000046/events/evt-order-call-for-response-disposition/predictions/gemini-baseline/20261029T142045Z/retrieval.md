# Retrieval Log

## 1. Path Resolution and CLI Help

- `uv run fedcourts paths --court scotus --docket 9026000046 --event evt-order-call-for-response-disposition --role predictor`
  - Resolved `case_id`: `scotus/9026000046`, `corpus`: `corpus/corpus.db`, `event`: `data/cases/scotus/9026000046/events/evt-order-call-for-response-disposition/event.yaml`.
- `uv run fedcourts query --help`
  - Inspected structured filter options for corpus retrieval.

## 2. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-238`
   - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned 1 row: `scotus/73275179` (*Cutberto Viramontes, et al. v. Cook County, Illinois, et al.*, No. 25-238, `disposition: "granted"`, `date_cert_granted: "2026-06-30"`, `distribution_count: 22`, petitioner counsel of record David H. Thompson).
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Returned 10 recent 2020s granted SCOTUS rows (including Nos. 26-12, 26-204, 25-1103, 25-7026, 25-1343, 25-1131, 25-1349, 26-104, and substantive applications 26A512 and 26A476).
3. `uv run fedcourts query --court scotus --citation "597 U.S. 1" --citation "577 U.S. 411"`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows (with note that only 200 SCOTUS rows in scope carry reporter citations).
4. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from prior cached pages)
   - Returned 10 recent 2020s SCOTUS GVR rows (Nos. 25-1269, 25-1367, 25-7569, 26-139, 26-5216, 25-901, 25-918, 25-7462, 25-7532, 26-48).
5. `uv run fedcourts query --court scotus --docket-number 24-1046`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: `scotus/72163396` (*Jason Wolford, et al. v. Anne E. Lopez, Attorney General of Hawaii*, No. 24-1046, `disposition: "granted"`, `date_cert_granted: "2025-10-03"`, `merits_decided: "2026-06-25"`, `merits_judgment: "reversed"`).
6. `uv run fedcourts query --court scotus --docket-number 24-203`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: `scotus/70436546` (*David Snope, et al. v. Anthony G. Brown, et al.*, No. 24-203, `disposition: "denied"`, `date_cert_denied: "2025-06-02"`, `distribution_count: 16`).
7. `uv run fedcourts query --court scotus --docket-number 24-131`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: `scotus/72483814` (*Ocean State Tactical, LLC, et al. v. Rhode Island, et al.*, No. 24-131, `disposition: "denied"`, `date_cert_denied: "2025-06-02"`, `distribution_count: 17`).

## 3. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Wolford v. Lopez", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=5)`
   - Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 7 seconds.`).
2. `mcp_courtlistener_search(type="o", court="ca2", case_name="United States v. Gomez", filed_after="2025-01-01", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=5)`
   - Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 6 seconds.`).
3. `mcp_courtlistener_search(type="o", case_name="Viramontes v. County of Cook", fields=["caseName", "dateFiled", "citation", "docketNumber", "court_id", "cluster_id"], num_results=5)`
   - Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 6 seconds.`).
4. `mcp_courtlistener_search(type="o", court="scotus", case_name="Wolford v. Lopez", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=5)` (retried after rate-limit window)
   - Failed with HTTP 502 Bad Gateway (`CourtListener API error: HTTP 502`).

## 4. Web Searches

- None attempted.
