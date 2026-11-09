# Retrieval Log

## 1. Corpus CLI Queries (`uv run fedcourts query`)

1. **Command:** `uv run fedcourts query --court scotus --docket-number 26-426`
   - **Transfer stderr:** `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - **Result:** Returned 1 row (`scotus/9026000426`, *Department of Homeland Security, et al. v. D. V. D., et al.*, docket `26-426`, `disposition: "granted"`, `date_cert_granted: "2026-09-29"`), confirming the grant of the overlapping § 1252(f)(1) / prospective class action case discussed in the cert reply.

2. **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - **Transfer stderr:** `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - **Result:** Returned 10 recently granted OT2026 SCOTUS petitions and applications, including several Solicitor General petitions granted after 2 distributions (`distribution_count: 2`, i.e., one relist), such as *Department of Justice v. McNutt* (`26-204`), *U.S. DOGE Service v. U.S. District Court for the District of Columbia* (`25-1103`), and *Blanche v. Ozurumba* (`25-1343`).

3. **Command:** `uv run fedcourts query --court scotus --judge "D. John Sauer" --limit 20`
   - **Transfer stderr:** `ranged corpus reads: 715 GET(s), 187432960 byte(s)`
   - **Result:** Returned 0 rows (since `--judge` matches panel/author judges on historical bulk rows rather than counsel of record).

4. **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - **Transfer stderr:** `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - **Result:** Returned 10 recently denied OT2026 SCOTUS cert petitions from the November 9, 2026 order list for comparison of distribution counts and counsel profiles.

## 2. CourtListener MCP Calls

1. **Tool:** `mcp_courtlistener_search` (`type: "d"`, `court: "scotus"`, `case_name: "Refugee and Immigrant Center for Education and Legal Services"`)
   - **Result:** `count: 0`, `results: []`.

2. **Tool:** `mcp_courtlistener_search` (`type: "d"`, `court: "scotus"`, `case_name: "D. V. D."`)
   - **Result:** `count: 0`, `results: []`.

## 3. Web Searches

None attempted.
