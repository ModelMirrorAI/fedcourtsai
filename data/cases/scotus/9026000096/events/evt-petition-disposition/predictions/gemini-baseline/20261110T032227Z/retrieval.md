# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. Companion docket lookup:
   - Command: `uv run fedcourts query --court "scotus" --docket-number "26-109"`
   - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned `scotus/9026000109` (*J.R. Simplot Company, LLC v. Shoshone-Bannock Tribes of the Fort Hall Reservation, et al.*, docketed 2026-07-23, distributed for conference 2026-12-04, `distribution_count = 1`).

2. Recent granted SCOTUS priors in the 2020s era:
   - Command: `uv run fedcourts query --court "scotus" --era "2020s" --disposition "granted" --limit 10`
   - Transfer line: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Result: Returned 10 recent OT2026 granted SCOTUS cases (including Solicitor General petitions such as `26-204`, `25-1103`, and `25-1343`).

## 2. CourtListener MCP Calls

1. Search for Ninth Circuit opinions in *Shoshone-Bannock Tribes*:
   - Tool: `mcp_courtlistener_search`
   - Parameters: `{"type": "o", "court": "ca9", "case_name": "Shoshone-Bannock Tribes", "fields": ["caseName", "dateFiled", "citation", "docketNumber", "judge", "cluster_id"]}`
   - Result: Found cluster `10658688` (2025-08-22 panel opinion, Docket No. 23-35543) and cluster `10846227` (2026-04-21 order denying rehearing en banc, Docket No. 23-35543).

2. Inspect cluster metadata for the April 21, 2026 order denying rehearing en banc:
   - Tool: `mcp_courtlistener_get_endpoint_item`
   - Parameters: `{"endpoint_id": "clusters", "item_id": 10846227, "fields": ["id", "case_name", "sub_opinions", "date_filed"]}`
   - Result: Identified sub-opinion `11313593`.

3. Read full text of the April 21, 2026 order and dissents from denial of rehearing en banc:
   - Tool: `mcp_courtlistener_read_document`
   - Parameters: `{"opinion_id": 11313593, "chunk_index": [0, 1, 2, 3], "chunk_size": 8000}`
   - Result: Retrieved Judge Collins's dissent from denial of rehearing en banc and Judge Tung's dissent from denial of rehearing en banc (joined by Judges Callahan, Bennett, R. Nelson, Bumatay, and VanDyke).

## 3. Web Searches

1. Check status of pending FY2027 NDAA legislation (S. 4784, § 1091(b)):
   - Tool: `google_web_search`
   - Query: `"S. 4784" "1091" OR "Blackrock Land Exchange" OR "Shoshone-Bannock" 2026`
   - Result: Confirmed that S. 4784 § 1091(b) remains a pending legislative proposal in the FY2027 NDAA after cloture failed in July 2026, and that No. 26-96 remains pending before the Supreme Court.
