# Retrieval Log (`scotus/9026000426` — `evt-brief-judgment`)

Mode: `forward` (`cutoff: 2026-11-17`). All external retrieval calls attempted during this run are logged below.

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000426" --event "evt-brief-judgment" --role predictor` and `uv run fedcourts query --help`
   - Result: Resolved case/event paths and CLI flags; no ranged corpus reads.
2. `uv run fedcourts query --court scotus --era Roberts --disposition reversed --limit 10`
   - Result: Failed with exit code 2 (`Unknown disposition 'reversed'; choose one of: granted, denied, granted-in-part, gvr, summary-reversal, dismissed, withdrawn, other`); no ranged corpus reads.
3. `uv run fedcourts query --court scotus --citation "609 U.S. 324"`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (with CLI note that only 195 SCOTUS rows carry reporter citations).
4. `uv run fedcourts query --court scotus --citation "606 U.S. 259"`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 0 rows returned.
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 38 GET(s), 9830400 byte(s)`
   - Result: Returned 10 recent OT2026 granted SCOTUS dockets/applications, including related executive/immigration matters (`Mullin v. RAICES`, No. 26-239, granted 2026-11-13; `Mullin v. Friends of the Ruidosa Church`, No. 26A560, granted 2026-11-09; `FCC v. Brown`, No. 26A476, granted 2026-10-14).

## 2. CourtListener MCP Lookups (20 calls)

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Homeland Security v. D. V. D.")` -> 0 results (`query_id: f8505764`).
2. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2025-10-01", q='"1252" OR "Mullin" OR "Blanche v. Lau"')` -> 9 results (`query_id: 30acc14a`), identifying OT2025 decisions `Blanche v. Lau` (`opinion_id=11346055`, 2026-06-23), `Mullin v. Doe` (`opinion_id=11347761`, 2026-06-25), `Mullin v. Al Otro Lado` (`opinion_id=11347762`, 2026-06-25), and `Trump v. Barbara` (`opinion_id=11351070`, 2026-06-30).
3. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2025-03-01", filed_before="2025-10-01", q='"A.A.R.P." OR "Riley v. Bondi" OR "Abrego Garcia" OR "J.G.G."')` -> 12 results (`query_id: c7778597`), identifying `A.A.R.P. v. Trump`, 605 U.S. 91 (`opinion_id=11052437`), `Riley v. Bondi`, 606 U.S. 259 (`opinion_id=11084446`), `Trump v. CASA, Inc.`, 606 U.S. 831 (`opinion_id=11112122`), and `Trump v. J.G.G.`, 604 U.S. 670 (`opinion_id=10891124`).
4. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2025-06-01", filed_before="2025-07-15", q='"D. V. D." OR "24A1153"')` -> 5 opinions citing the June/July 2025 `D.V.D.` stay orders (`query_id: 7a8a4394`).
5. `mcp_courtlistener_read_document(opinion_id=11347761, chunk_index=0)` -> `Mullin v. Doe`, 609 U.S. 324 (2026), syllabus Part 1 (TPS judicial-review bar holding).
6. `mcp_courtlistener_read_document(opinion_id=11347762, chunk_index=0)` -> `Mullin v. Al Otro Lado`, 609 U.S. 258 (2026), syllabus Part 1 (INA border arrival holding and non-mootness due to declaratory judgment).
7. `mcp_courtlistener_read_document(opinion_id=11346055, chunk_index=0)` -> `Blanche v. Lau`, 609 U.S. 1 (2026), syllabus Part 1 (INA LPR parole/removal holding).
8. `mcp_courtlistener_read_document(opinion_id=11084446, chunk_index=0)` -> `Riley v. Bondi`, 606 U.S. 259 (2025), syllabus Part 1 (`§ 1252(b)(1)` and withholding-only orders).
9. `mcp_courtlistener_read_document(opinion_id=11347761, chunk_index=1)` -> `Mullin v. Doe` vote lineup (`6–3`, Alito for the Court; Gorsuch and Barrett not joining Part III-A; Thomas concurring; Kagan dissenting with Sotomayor and Jackson).
10. `mcp_courtlistener_read_document(opinion_id=11347762, chunk_index=1)` -> `Mullin v. Al Otro Lado` vote lineup (`6–3`, Alito for the Court; Thomas concurring; Sotomayor dissenting with Kagan and Jackson).
11. `mcp_courtlistener_read_document(opinion_id=11346055, chunk_index=1)` -> `Blanche v. Lau` vote lineup (`6–3`, Thomas for the Court; Sotomayor dissenting with Kagan and Jackson).
12. `mcp_courtlistener_read_document(opinion_id=11084446, chunk_index=1)` -> `Riley v. Bondi` vote lineup (`5–4` on Part II-A with Gorsuch dissenting alongside Sotomayor, Kagan, and Jackson on CAT/withholding PFR timing; `9–0` on Part II-B).
13. `mcp_courtlistener_read_document(opinion_id=11052437, chunk_index=0)` -> `A.A.R.P. v. Trump`, 605 U.S. 91 (2025), `7–2` per curiam holding on AEA removal notice; Kavanaugh concurring; Alito and Thomas dissenting.
14. `mcp_courtlistener_read_document(opinion_id=11112122, chunk_index=[0, 1])` -> `Trump v. CASA, Inc.`, 606 U.S. 831 (2025), `6–3` opinion by Barrett on equitable remedial limits; Thomas, Alito, and Kavanaugh concurring; Sotomayor and Jackson dissenting.
15. `mcp_courtlistener_search_document(opinion_id=11347761, query="Part III")` -> 4 snippets in `Mullin v. Doe` locating Part III-A (`Trump v. Hawaii` constitutional review standard).
16. `mcp_courtlistener_search_document(opinion_id=11347761, query="705")` -> 2 snippets in `Mullin v. Doe` confirming the Court avoided resolving APA `§ 705` scope.
17. `mcp_courtlistener_search(type="o", citation="145 S. Ct. 2153")` -> 1 unrelated 1892 opinion (`Kissam v. Anderson`; `query_id: 32b86344`).
18. `mcp_courtlistener_search(type="o", citation="145 S. Ct. 2627")` -> 0 results (`query_id: 67d180be`).
19. `mcp_courtlistener_read_document(opinion_id=11347761, chunk_index=[6, 7, 8])` -> `Mullin v. Doe` Part III-A text showing why Gorsuch and Barrett declined to join Part III-A.
20. `mcp_courtlistener_read_document(opinion_id=11351070, chunk_index=[0, 1])` -> `Trump v. Barbara` returned `"No text is available for this document."`

## 3. Official Docket Check (`web_fetch`)

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-426.html`
   - Result: Confirmed oral argument remains set for December 9, 2026 and no docket entries postdate Respondents' November 16, 2026 merits brief as of November 23, 2026. No commentary or external forecasts were searched or accessed.

## How Retrieval Informed the Forecast

- Inspecting the OT2024–OT2025 Supreme Court opinions (`Mullin v. Doe`, `Mullin v. Al Otro Lado`, `Blanche v. Lau`, `Riley v. Bondi`, `A.A.R.P. v. Trump`, and `Trump v. CASA, Inc.`) sharpened three parts of the forecast: (1) confirming the consistent `6–3` conservative lineup and `Reversed and remanded` judgment form in argued immigration/remedies challenges; (2) identifying Justice Alito's heavy authorship concentration in INA `§ 1252` / removal cases alongside Roberts, Barrett, and Kavanaugh; and (3) highlighting Justice Gorsuch's `Riley` partial dissent and Gorsuch/Barrett's narrower join in `Mullin v. Doe`, which makes a `§ 1252(f)(1)` + facial-merits holding likelier to hold all six conservatives than a total `§ 1252(b)(9)` forum bar and raises Gorsuch's and Thomas's separate-writing probabilities.
