# Retrieval Log

## 1. Corpus Lookups (`uv run fedcourts query`)

1. **Recent SCOTUS granted priors (2020s era)**:
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
   - Result: Returned 10 recent OT2026/2020s granted petitions and applications (including *Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12; *DOJ v. McNutt*, No. 26-204; *U.S. DOGE Service v. USDC D.C.*, No. 25-1103).

2. **Recent SCOTUS denied priors (2020s era)**:
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned 10 recent 2020s denied petitions and applications.

3. **Fourth Circuit judge filter lookup**:
   - Command: `uv run fedcourts query --court ca4 --judge Quattlebaum --judge King --limit 10`
   - Transfer: `ranged corpus reads: 93 GET(s), 24379392 byte(s)`
   - Result: Empty (as noted in `.github/prompts/predict.md`, circuit slice judge lists are withheld).

4. **SCOTUS standing precedent citation lookup**:
   - Command: `uv run fedcourts query --court scotus --citation "603 U.S. 43" --citation "602 U.S. 367" --citation "588 U.S. 752" --limit 10`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned *Department of Commerce v. New York*, 588 U.S. 752 (2019) (`scotus/15006775`, No. 18-966).

5. **Docket lookup for No. 26-60**:
   - Command: `uv run fedcourts query --court scotus --docket-number 26-60`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned corpus row for `scotus/9026000060` (*Daniel Defense, LLC, et al. v. Karen Lowy, et al.*), unresolved (`disposition: null`).

## 2. CourtListener MCP Lookups

1. **Search for Fourth Circuit opinion (*Lowy v. Daniel Defense*)**:
   - Tool: `mcp_courtlistener_search` (`type: "o"`, `court: "ca4"`, `case_name: "Lowy v. Daniel Defense"`)
   - Result: `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 641 seconds.'}`

2. **Search for SCOTUS docket (*Daniel Defense v. Lowy*)**:
   - Tool: `mcp_courtlistener_search` (`type: "d"`, `court: "scotus"`, `case_name: "Daniel Defense v. Lowy"`)
   - Result: `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 641 seconds.'}`

## 3. Web Searches

None attempted.
