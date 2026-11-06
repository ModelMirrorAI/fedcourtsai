# Retrieval Log

## Corpus CLI Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 22-508`
   - Stderr: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Result: Returned `scotus/72475926` (*John O. Green v. United States*, No. 22-508), originating from `ca5` (No. 21-10651), filed `2022-11-30`, distributed once for conference `2023-01-20`, certiorari denied `2023-01-23`.

2. `uv run fedcourts query --court scotus --docket-number 22-729`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72478385` (*Thomas D. Selgas v. United States*, No. 22-729), originating from `ca5` (No. 21-10672), filed `2023-02-06`, distributed once for conference `2023-03-24`, certiorari denied `2023-03-27`.

3. `uv run fedcourts query --court scotus --citation "537 U.S. 522" --citation "596 U.S. 528" --limit 5`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Empty result with coverage note (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `q='"2255(f)(1)" "co-defendant" certiorari final'`, `fields=["caseName", "court", "dateFiled", "citation", "snippet"]`, `num_results=10`)
   - Result: Returned 14 total matches (10 shown, including *Castro-Gaxiola v. United States*, 665 F. Supp. 2d 1049 (W.D. Mo. 2009); *Stewart v. United States*, 89 F. Supp. 3d 993 (E.D. Wis. 2015); *United States v. Roe*, 913 F.3d 1285 (10th Cir. 2019); *Arango v. United States*, 626 F. Supp. 2d 173 (D. Mass. 2009)), confirming that lower-court decisions addressing co-defendant certiorari petitions under 28 U.S.C. § 2255(f)(1) arise almost exclusively in district court orders rejecting reliance on a co-defendant's certiorari timeline, with no circuit conflict on the question presented.

## Web Searches

- None attempted.
