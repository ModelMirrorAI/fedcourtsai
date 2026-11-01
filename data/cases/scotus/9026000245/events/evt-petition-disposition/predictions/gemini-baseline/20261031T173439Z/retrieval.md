# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 23-9`
   - Stderr/transfer: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: 1 row returned (`scotus/72483367`, *AstraZeneca UK Limited, et al. v. Joshua Atchley, et al.*, No. 23-9, filed 2023-07-05, CVSG 2023-10-02, distributed twice, GVR'd 2024-06-24).

2. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - Stderr/transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 10 recent 2020s SCOTUS GVR priors returned (`scotus/73317900`, `scotus/73500268`, `scotus/73500579`, `scotus/9026000139`, `scotus/9026005216`, `scotus/73280412`, `scotus/73280426`, `scotus/73393227`, `scotus/73500363`, `scotus/9026000048`).

3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Stderr/transfer: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Result: 10 recent 2020s SCOTUS granted priors returned (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`).

4. `uv run fedcourts query --court scotus --attorney "Lisa S. Blatt" --limit 20` (failed — unsupported flag)
   - Result: Usage error (`No such option: --attorney`).

5. `uv run fedcourts query --court scotus --party "Deutsche Bank" --limit 20` (failed — unsupported flag)
   - Result: Usage error (`No such option: --party`).

6. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 10`
   - Stderr/transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 10 recent 2020s SCOTUS denied priors returned (`scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9526000555`, `scotus/9526000556`, `scotus/9526000416`, `scotus/9526000545`, `scotus/9026005865`, `scotus/9526000524`, `scotus/9526000530`).

7. `uv run fedcourts query --court scotus --docket-number 25-713`
   - Stderr/transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: 1 row returned (`scotus/73279562`, *George Barry Hawkins, Jr. v. Abigail Spanberger*, denied 2026-02-23).

8. `uv run fedcourts query --court scotus --docket-number 24-856`
   - Stderr/transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: 1 row returned (`scotus/72487129`, *Cisco Systems, Inc., et al. v. Doe I, et al.*, granted 2026-01-09, merits decided 2026-06-23, reversed).

9. `uv run fedcourts query --court scotus --docket-number 23-1141`
   - Stderr/transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: 1 row returned (`scotus/69702989`, *Smith & Wesson Brands, Inc., et al. v. Estados Unidos Mexicanos*, granted 2024-10-04, merits decided 2025-06-05, reversed).

10. `uv run fedcourts query --court scotus --docket-number 25-710` / `25-711` / `25-712` / `25-714` / `25-715`
    - Stderr/transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (for each of the 5 queries)
    - Result: 1 row each (`scotus/73279559`, `scotus/73279560`, `scotus/73279561`, `scotus/73279563`, `scotus/73279565`), all denied in early 2026.

11. `uv run fedcourts query --court scotus --docket-number 25-773` / `25-723` / `25-613` / `25-513` / `25-813` / `25-718` / `25-719`
    - Stderr/transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25-773` and `25-513`); `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-723`, `25-613`, `25-813`, `25-718`, `25-719`)
    - Result: 1 row each (`scotus/73279904`, `scotus/73279572`, `scotus/73279057`, `scotus/73278953`, `scotus/73279946`, `scotus/73279568`, `scotus/73279569`), all denied.

12. `uv run fedcourts query --court scotus --docket-number 24-713` / `25-413` / `25-313` / `25-913` / `25-173`
    - Stderr/transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `24-713` and `25-313`); `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-413`, `25-913`, `25-173`)
    - Result: 1 row each (`scotus/72486579`, `scotus/73278435`, `scotus/73277389`, `scotus/73280421`, `scotus/73274857`), all denied.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="Ashley v. Deutsche Bank")`
   - Result: 0 results (indexed under *Wildman v. Deutsche Bank*).

2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Cisco Systems v. Doe")`
   - Result: 1 result (`opinion_id=11346054`, *Cisco Systems, Inc. v. Doe*, decided 2026-06-23).

3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Smith & Wesson v. Estados Unidos Mexicanos")`
   - Result: 2 results (`opinion_id=11065593`, *Smith & Wesson Brands, Inc. v. Estados Unidos Mexicanos*, 605 U.S. 280, decided 2025-06-05).

4. `mcp_courtlistener_search(type="d", case_name="AstraZeneca v. Atchley")`
   - Result: 3 D.C. Circuit / D.D.C. dockets (`20-7077`, `1:17-cv-02136`).

5. `mcp_courtlistener_read_document(opinion_id=11346054, chunk_index=0)`
   - Result: Read syllabus of *Cisco Systems, Inc. v. Doe* (2026).

6. `mcp_courtlistener_search(type="o", citation="144 F.4th 420")`
   - Result: 0 results by F.4th reporter citation.

7. `mcp_courtlistener_search(type="o", court="ca2", q='"Taamneh" "Deutsche Bank"')`
   - Result: 1 result (`opinion_id=11104289`, *Wildman v. Deutsche Bank* / *Ashley v. Deutsche Bank*, No. 23-132, decided 2025-07-16).

8. `mcp_courtlistener_search_document(opinion_id=11346054, query="Taamneh")`
   - Result: 15 matches in *Cisco Systems, Inc. v. Doe* discussing *Twitter v. Taamneh*.

9. `mcp_courtlistener_search(type="o", court="cadc", docket_number="20-7077")`
   - Result: 2 results (*Atchley I*, 2022, and *Atchley II*, `opinion_id=11245308`, 2026-02-06).

10. `mcp_courtlistener_read_document(opinion_id=11104289, chunk_index=0)`
    - Result: Read opening section of *Wildman v. Deutsche Bank* (2d Cir. 2025).

11. `mcp_courtlistener_search(type="d", court="scotus", case_name="Ashley v. Deutsche Bank")`
    - Result: 0 results.

12. `mcp_courtlistener_search(type="d", court="scotus", q='"Deutsche Bank" "Taamneh"')`
    - Result: 0 results.

13. `mcp_courtlistener_read_document(opinion_id=11346054, chunk_index=1)`
    - Result: Read beginning of majority opinion in *Cisco Systems, Inc. v. Doe* (2026).

14. `mcp_courtlistener_read_document(opinion_id=11104289, chunk_index=[10, 11, 12, 13])`
    - Result: Read JASTA aiding-and-abetting analysis in *Wildman v. Deutsche Bank* (2d Cir. 2025).

15. `mcp_courtlistener_read_document(opinion_id=11346054, chunk_index=[5, 6, 7])`
    - Result: Read *Taamneh* and *Central Bank* discussion in *Cisco Systems, Inc. v. Doe* (2026).

16. `mcp_courtlistener_read_document(opinion_id=11065593, chunk_index=[0, 1, 2])` and `chunk_index=[3, 4, 5, 6, 7]`
    - Result: Read full opinion in *Smith & Wesson Brands, Inc. v. Estados Unidos Mexicanos* (2025).
