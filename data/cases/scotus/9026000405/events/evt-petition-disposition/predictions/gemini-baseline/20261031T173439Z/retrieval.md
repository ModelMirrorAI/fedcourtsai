# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer stderr: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Returned 10 recent 2020s SCOTUS granted petitions and substantive applications (including OT2026 grants such as *Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12; *Department of Justice v. McNutt*, No. 26-204; and *Rhoney v. Barbosa da Cunha*, No. 26-104) to review recent OT2026 cert grant patterns and salience scores.

2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent 2020s SCOTUS denied petitions and applications from the warm local corpus service cache.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `q=""Daniels-Lumley" OR ("substantial question" AND "8102" AND "FECA")"`, `num_results=10`)
   - Returned 76 total matches (10 shown), including the district court opinion in this case (*He v. Blinken*, No. 22-1137, 2023-11-13), *Daniels-Lumley v. United States*, 306 F.2d 769 (D.C. Cir. 1962), *Bruni v. United States*, 964 F.2d 76 (1st Cir. 1992), and recent D.D.C. decisions applying *Daniels-Lumley*.

2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Federal Employees' Compensation Act" "substantial question" OR "8128(b)""`, `num_results=10`)
   - Returned 27 total matches (10 shown), including *Southwest Marine, Inc. v. Gizoni*, 502 U.S. 81 (1991), and *Lockheed Aircraft Corp. v. United States*, 460 U.S. 190 (1983), confirming that the Supreme Court has not recently granted certiorari on the FECA "substantial question" primary-jurisdiction doctrine.

3. `mcp_courtlistener_search` (`type="o"`, `q=""Moe v. United States" "326 F.3d 1065" OR "Fuqua v. United States Postal""`, `num_results=10`)
   - Returned 22 total matches (10 shown), including *Moe v. United States*, 326 F.3d 1065 (9th Cir. 2003), the Supreme Court's denial of certiorari in *Moe v. United States*, 540 U.S. 877 (2003), and *Hawkins v. United States*, 14 F.4th 1018 (9th Cir. 2021).

4. `mcp_courtlistener_search` (`type="o"`, `citation="14 F.4th 1018"`, `num_results=5`)
   - Resolved opinion ID `5125330` for *Sabelita Hawkins v. United States*, 14 F.4th 1018 (9th Cir. 2021).

5. `mcp_courtlistener_read_document` (`opinion_id=5125330`)
   - Read the full text of *Hawkins v. United States*, 14 F.4th 1018 (9th Cir. 2021), where the Ninth Circuit held that after a federal employee submitted a FECA claim for workplace harassment and OWCP denied it as not sustained in the performance of duty, the employee was free to pursue an FTCA suit.

6. `mcp_courtlistener_read_document` (`opinion_id=781702`)
   - Read the full text of *Moe v. United States*, 326 F.3d 1065 (9th Cir. 2003), confirming that the Ninth Circuit cites *Reep v. United States*, 557 F.2d 204, 208 (9th Cir. 1977), for the "substantial question" doctrine on performance-of-duty questions and holds that psychological injury accompanied by physical injury is within FECA's scope.
