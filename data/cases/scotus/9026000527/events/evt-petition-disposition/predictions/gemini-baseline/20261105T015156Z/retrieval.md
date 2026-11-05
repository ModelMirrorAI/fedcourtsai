# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. Lookup of Petitioner's prior stay application (`26A263`) referenced in the petition's statement of related proceedings:
   - Command: `uv run fedcourts query --court scotus --docket-number 26A263 --limit 5`
   - Transfer stderr: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - Result: Returned 1 row (`scotus/9526000263`, *Cesari S.R.L. v. Peju Province Winery L.P., et al.*, docket `26A263`, filed `2026-08-27`, decided `2026-08-28`, `disposition: "denied"`).

2. Lookup of *RiseandShine Corporation v. PepsiCo, Inc.* (`24-1016`), cited in the petition as a pending Second Circuit trademark case:
   - Command: `uv run fedcourts query --court scotus --docket-number 24-1016 --limit 5`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/72483489`, *RiseandShine Corporation, dba Rise Brewing v. PepsiCo, Inc.*, docket `24-1016`, `date_cert_granted: "2026-06-29"`, `disposition: "granted"`).

3. Lookup of *B&B Hardware, Inc. v. Hargis Industries, Inc.* (`575 U.S. 138` / `135 S. Ct. 1293`) by reporter citation:
   - Command: `uv run fedcourts query --court scotus --citation "575 U.S. 138" --citation "135 S. Ct. 1293" --limit 5`
   - Transfer stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (printed `note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

4. Lookup of SCOTUS cert petitions with overlap on Second Circuit panel judges (`Richard C. Wesley`, `Richard J. Sullivan`, `Joseph F. Bianco`):
   - Command: `uv run fedcourts query --court scotus --judge "Richard C. Wesley" --judge "Richard J. Sullivan" --judge "Joseph F. Bianco" --limit 10`
   - Transfer stderr: `ranged corpus reads: 679 GET(s), 177799168 byte(s)`
   - Result: 0 rows returned (live-channel SCOTUS rows do not populate lower-court panel judges in `--judge`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Cesari Peju"`, `num_results=10`)
   - Result: 0 hits (`query_id: "ab7547d4"`).

2. `mcp_courtlistener_search` (`type="o"`, `citation="575 U.S. 138"`, `num_results=5`)
   - Result: 4 hits (`query_id: "7cc4e1a6"`), including *B&B Hardware, Inc. v. Hargis Industries, Inc.*, 575 U.S. 138 (2015) (`cluster_id: 2789598`, lead opinion `9812717` by Justice Alito, concurrence `9812718` by Justice Ginsburg, dissent `9812719` by Justice Thomas).

3. `mcp_courtlistener_search` (`type="o"`, `q='"Cesari" "Peju"'`, `num_results=10`)
   - Result: 0 hits (`query_id: "c769e7fd"`).

4. `mcp_courtlistener_search` (`type="o"`, `q='"B&B Hardware" "Levy" "Kosher Overseers"'`, `num_results=10`)
   - Result: 0 hits (`query_id: "2d9d744d"`).

5. `mcp_courtlistener_read_document` (`opinion_id=9812718`)
   - Result: Read full text (`62,690` chars) of Justice Ginsburg's concurrence and Justice Thomas's dissent in *B&B Hardware, Inc. v. Hargis Industries, Inc.*, 575 U.S. 138 (2015).

6. `mcp_courtlistener_search_document` (`opinion_id=9812717`, `query="marketplace usage"`)
   - Result: 1 match at position `59909` in Justice Alito's opinion for the Court in *B&B Hardware*.

7. `mcp_courtlistener_read_document` (`opinion_id=9812717`, `chunk_index=[6, 7, 8]`, `chunk_size=8000`)
   - Result: Read Parts III–IV of Justice Alito's opinion for the Court in *B&B Hardware*, 575 U.S. at 151–60.

8. `mcp_courtlistener_read_document` (`opinion_id=9812717`, `chunk_index=9`, `chunk_size=8000`)
   - Result: Read Part V and footnotes 1–4 of Justice Alito's opinion for the Court in *B&B Hardware*, 575 U.S. at 160.

9. `mcp_courtlistener_search` (`type="o"`, `citation="823 F.3d 153"`, `num_results=5`)
   - Result: 1 hit (`query_id: "487fd2bf"`): *International Information Systems Security Certification Consortium, Inc. v. Security University, LLC*, 823 F.3d 153 (2d Cir. 2016) (`opinion_id: 8413986`).

10. `mcp_courtlistener_search` (`type="o"`, `citation="104 F.3d 38"`, `num_results=5`)
    - Result: 7 hits (`query_id: "5a07b2ba"`), including *Levy v. Kosher Overseers Ass'n of America, Inc.*, 104 F.3d 38 (2d Cir. 1997) (`opinion_id: 6944162`).

11. `mcp_courtlistener_search_document` (`opinion_id=8413986`, `query="Levy"`)
    - Result: 9 snippet matches in *International Information Systems Security Certification Consortium*, 823 F.3d at 156, 163–64, showing the Second Circuit's citation of *Levy*.

## 3. Web Searches
- None attempted.
