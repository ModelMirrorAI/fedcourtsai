# Retrieval Log

## 1. Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-238`
   - `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Returned the SCOTUS corpus record for *Cutberto Viramontes, et al. v. Cook County, Illinois, et al.* (`scotus/73275179`), confirming cert grant on `2026-06-30`, originating court `ca7` (`24-1437`), and party/amicus counsel entries.
2. `uv run fedcourts query --court scotus --docket-number 25-566`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned the SCOTUS corpus record for consolidated companion *Eddie Grant, Jr., et al. v. Ronnell Higgins, et al.* (`scotus/73279009`), originating court `ca2` (`23-1344`), cert granted `2026-06-30`.
3. `uv run fedcourts query --court scotus --docket-number 24-1046`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned *Jason Wolford, et al. v. Anne E. Lopez, Attorney General of Hawaii* (`scotus/72163396`), decided `2026-06-25`, `merits_judgment: "reversed"`.
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 50`
   - `ranged corpus reads: 62 GET(s), 16252928 byte(s)`
   - Returned 50 recent 2020s SCOTUS granted cases for general merits context.
5. `uv run fedcourts query --court scotus --docket-number 24-1234`
   - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned *United States v. Ali Danial Hemani* (`scotus/72350770`), decided `2026-06-18`, `merits_judgment: "affirmed"`.
6. `uv run fedcourts query --court scotus --docket-number 22-915`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned *United States v. Zackey Rahimi* (`scotus/67986093`), decided `2024-06-21`, `merits_judgment: "reversed"`.
7. `uv run fedcourts query --court scotus --docket-number 22-976`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned *Merrick B. Garland, Attorney General, et al. v. Michael Cargill* (`scotus/68305308`), decided `2024-06-14`, `merits_judgment: "affirmed"`.
8. `uv run fedcourts query --court scotus --docket-number 23-852`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned *Pamela Bondi, Attorney General, et al. v. Jennifer VanDerStok, et al.* (`scotus/69235413`), decided `2025-03-26`, `merits_judgment: "reversed"`.
9. `uv run fedcourts query --court scotus --docket-number 23-1141`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned *Smith & Wesson Brands, Inc., et al. v. Estados Unidos Mexicanos* (`scotus/69702989`), decided `2025-06-05`, `merits_judgment: "reversed"`.
10. `uv run fedcourts query --court scotus --originating-court ca7 --disposition granted --era 2020s --limit 50`
    - Refused with usage error (`No such option: --originating-court`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Wolford v. Lopez", filed_before="2026-10-22")`
   - Returned cluster `10880241` / opinion `11347760` (*Wolford v. Lopez*, filed `2026-06-25`).
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="United States v. Hemani", filed_before="2026-10-22")`
   - Returned cluster `10876933` / opinion `11344434` (*United States v. Hemani*, filed `2026-06-18`).
3. `mcp_courtlistener_search(type="o", court="ca3", case_name="Association of New Jersey Rifle", filed_before="2026-10-22")`
   - Returned cluster `11011466` / opinion `11400454` (*Association of New Jersey Rifle and Pistol Clubs Inc. v. Attorney General New Jersey*, 3d Cir. en banc, filed `2026-09-11`).
4. `mcp_courtlistener_search(type="o", court="ca7", case_name="Barnett v. Raoul", filed_before="2026-10-22")`
   - Returned cluster `11011495` / opinion `11400484` (*Caleb Barnett v. Kwame Raoul*, 7th Cir., filed `2026-07-20`) and cluster `9437263` (*Bevis v. City of Naperville* / *Barnett v. Raoul*, 85 F.4th 1175, filed `2023-11-03`).
5. `mcp_courtlistener_read_document(opinion_id=11347760, chunk_index=0..4)`
   - Read the syllabus and majority opinion opening/step-one framework of *Wolford v. Lopez* (609 U.S. ___, June 25, 2026, Alito, J., for a 6–3 Court).
6. `mcp_courtlistener_read_document(opinion_id=11344434, chunk_index=0)`
   - Returned `"No text is available for this document."`
7. `mcp_courtlistener_search_document(opinion_id=[11347760, 11344434], query="common use")` and `query="dangerous and unusual"`
   - Returned 0 literal matches in `11347760` and no text available for `11344434`.
8. `mcp_courtlistener_read_document(opinion_id=11400454, chunk_index=0..11)`
   - Read the Third Circuit en banc majority opinion in *Association of New Jersey Rifle and Pistol Clubs Inc. v. Attorney General New Jersey* (Sept. 11, 2026), applying *Wolford*, *Bruen*, and *Heller* to invalidate New Jersey's AR-15 ban.
9. `mcp_courtlistener_read_document(opinion_id=11400484, chunk_index=0)`
   - Read the opening of the Seventh Circuit's final-judgment decision in *Barnett v. Raoul* (July 20, 2026).
10. `mcp_courtlistener_search(type="o", court="scotus", q="Hemani", filed_before="2026-10-22")`
    - Returned 5 results (including `10876933` and prior orders).
11. `mcp_courtlistener_search(type="o", court="scotus", case_name="Snope v. Brown", filed_before="2026-10-22")`, `case_name="Harrel v. Raoul"`, and `court="ca2", case_name="National Association for Gun Rights v. Lamont"`
    - Returned 0 results (citations and excerpts were read directly from the provisioned briefs).
