# Retrieval Log

## 1. `fedcourts` CLI Corpus Queries

1. `uv run fedcourts query --court scotus --citation "489 U.S. 538" --limit 5`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: 0 rows returned (note printed explaining that only 200 SCOTUS rows carry parallel reporter citations in the `citations` column).
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: Returned 5 recent 2020s SCOTUS denial rows (`scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9526000555`, `scotus/9526000556`) showing `sal-v4` salience scoring and docket metadata structure.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `q=""Blanton" "922(g)(9)" OR "domestic violence" "jury trial" "six months" "Second Amendment""`, `num_results=10`)
   - Result: 3 matches returned (`Baginski v. Lynch`, 229 F. Supp. 3d 48 (D.D.C. 2017); `United States v. Chavez`, 204 F.3d 1305 (11th Cir. 2000) [two entries]).
2. `mcp_courtlistener_search` (`type="o"`, `q=""448 P.3d 1120" OR "135 Nev. 321" OR ("Blanton" "922(g)(9)")"`, `num_results=10`)
   - Result: 11 matches returned, including Nevada Supreme Court decisions applying *Andersen v. Eighth Judicial District Court*, 448 P.3d 1120 (Nev. 2019), and `Medhin v. United States`, No. 22-CM-0611 (D.C. Feb. 8, 2024) (`opinion_id=9931045`).
3. `mcp_courtlistener_read_document` (`opinion_id=9931045`, `chunk_index=0`)
   - Result: Read first chunk of *Medhin v. United States* (D.C. 2024), addressing whether a firearm prohibition triggered by an intrafamily misdemeanor offense creates a Sixth Amendment jury-trial right under *Blanton*.
4. `mcp_courtlistener_read_document` (`opinion_id=9931045`, `chunk_index=[2, 3]`)
   - Result: Read chunks 2–3 of *Medhin v. United States* (D.C. 2024), discussing *Blanton*, *Heller*, *Bruen*, and distinguishing *Andersen v. Eighth Judicial District Court*, 448 P.3d 1120 (Nev. 2019), on the ground that Nevada's firearm ban was permanent whereas D.C.'s ban was temporary.
5. `mcp_courtlistener_search` (`type="o"`, `q=""204 F.3d 1305""`, `num_results=5`)
   - Result: Located opinion ID `74349` for *United States v. Chavez*, 204 F.3d 1305 (11th Cir. 2000).
6. `mcp_courtlistener_read_document` (`opinion_id=74349`)
   - Result: Read *United States v. Chavez*, 204 F.3d 1305 (11th Cir. 2000), holding that 18 U.S.C. § 922(g)(9)'s firearm prohibition is a collateral consequence that does not convert a petty domestic violence offense into a serious one under *Blanton*, especially given 18 U.S.C. § 921(a)(33)(B)(i)(II).

## 3. Web Searches

- None attempted.
