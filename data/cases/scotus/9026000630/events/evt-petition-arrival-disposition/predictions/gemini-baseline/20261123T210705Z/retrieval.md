# Retrieval Log (`scotus/9026000630` / `evt-petition-arrival-disposition`)

Mode: `forward` (`cutoff: 2026-11-14`, `decided_before: null`). No third-party forecasts or odds were searched for or encountered.

## 1. CLI & Corpus Queries (`uv run fedcourts ...`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000630" --event "evt-petition-arrival-disposition" --role predictor && uv run fedcourts query --help`
   - Stderr transfer line: none (path resolution and CLI help inspection).
   - Returned predictor paths and `fedcourts query` flag documentation.
2. `python3 -c 'import subprocess; p = subprocess.run(["uv", "run", "fedcourts", "query", "--help"], capture_output=True, text=True); print(p.stdout)'`
   - Stderr transfer line: none (full `--help` inspection).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15 2>&1`
   - Stderr transfer line: `ranged corpus reads: 44 GET(s), 11403264 byte(s)`
   - Returned 15 recent 2020s SCOTUS granted petitions, identifying `scotus/9026000104` (*Philip L. Rhoney v. Ricardo Aparecido Barbosa da Cunha*, No. 26-104, cert granted `2026-10-01`, same petitioner counsel D. John Sauer and respondent counsel Michael King Thomas Tan).
4. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10 2>&1`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 Fall 2026 SCOTUS GVR dispositions (`distribution_count` of 2 on nearly all held GVRs).
5. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 30 2>&1`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 30 recent open and resolved OT2026 SCOTUS dockets and applications.
6. `uv run fedcourts query --court scotus --era 2020s --include-open --attorney "D. John Sauer" --limit 35 2>&1`
   - Failed with CLI usage error (`No such option: --attorney`); no corpus read.
7. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --decided-before 2026-08-01 --limit 25 2>&1`
   - Stderr transfer line: `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   - Returned 25 June 2026 end-of-Term cleanup GVR cases, all showing `distribution_count >= 2`.
8. `uv run fedcourts query --court scotus --docket-number 25-1415 --include-open 2>&1`
   - Stderr transfer line: `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
   - Returned `scotus/73529868` (*Putra v. Lopez-Campos*, No. 25-1415, open SG hold petition on § 1225(b)(2)(A), distributed `2026-09-28`, `distribution_count: 1`).
9. `uv run fedcourts query --court scotus --docket-number 26-568 --include-open 2>&1`
   - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9026000568` (*Quinones v. Rodriguez Vazquez*, No. 26-568, open SG hold petition filed `2026-10-29`).
10. `uv run fedcourts query --court scotus --docket-number 26-572 --include-open 2>&1`
    - Stderr transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned `scotus/9026000572` (*Padula v. Cirrus Rojas*, No. 26-572, open SG hold petition distributed for `2026-12-04`, `distribution_count: 1`).
11. `uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026-07-05 --limit 20 2>&1`
    - Stderr transfer line: `ranged corpus reads: 43 GET(s), 11141120 byte(s)`
    - Returned 20 end-of-Term June/July 2026 denied dockets, confirming that held-then-denied petitions cleaned up on June 30, 2026 (including First Circuit SG hold petition *Trump v. O. Doe*, No. 25-899) recorded `distribution_count >= 2`.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca1", case_name="Guerrero Orellana", ...)` (`query_id: ad31a5be`) -> 1 result: *Guerrero Orellana v. Moniz*, Nos. 25-2152, 26-1094 (1st Cir. Aug. 13, 2026), cluster `10947821`, opinion `11415407` (published).
2. `mcp_courtlistener_search(type="r", court="ca1", docket_number="25-2152", ...)` (`query_id: b22130da`) -> 1 result: CA1 docket `71992218`.
3. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 71992218, ...}, num_results=50)` (`query_id: 48af10da`) -> returned CA1 docket entries through `2026-11-13` (Supreme Court notice of cert petition filing; no rehearing en banc sought).
4. `mcp_courtlistener_read_document(opinion_id=11415407, chunk_index=[0,1,2,3], chunk_size=8000)` -> read opening background, class posture, and statutory framing of *Guerrero Orellana v. Moniz*.
5. `mcp_courtlistener_search(type="o", case_name="Barbosa da Cunha", ...)` (`query_id: 58edc412`) -> 1 result: *Barbosa Da Cunha v. Freden*, No. 25-3141 (2d Cir. Sept. 25, 2026 order), cluster `10983473`, opinion `11451136`.
6. `mcp_courtlistener_search(type="o", q=""Yajure Hurtado"")` (`query_id: aba965c1`) -> 20 results including *Matter of Yajure Hurtado*, 29 I. & N. Dec. 216 (BIA 2025) (`10669471`) and appellate/district § 1225(b)(2)(A) decisions.
7. `mcp_courtlistener_search_document(opinion_id=11415407, query="Barbosa")` -> 4 matches in *Guerrero Orellana* citing *Barbosa da Cunha v. Freden*, 175 F.4th 61 (2d Cir. 2026).
8. `mcp_courtlistener_read_document(opinion_id=11415407, chunk_index=[14,15,16,17,18,19,20,21], chunk_size=8000)` -> read conclusion of majority opinion and Judge Dunlap's dissent in *Guerrero Orellana*.
9. `mcp_courtlistener_read_document(opinion_id=11451136, chunk_index=[0,1], chunk_size=8000)` -> returned error `"No text is available for this document."`
10. `mcp_courtlistener_read_document(opinion_id=11415407, chunk_index=[4,5,6], chunk_size=8000)` -> read First Circuit textual analysis of § 1225(b)(2)(A)'s "seeking admission" clause.
11. `mcp_courtlistener_search(type="o", case_name="Buenrostro-Mendez", ...)` (`query_id: 31b8d76c`) -> 0 results.
12. `mcp_courtlistener_search(type="o", case_name="Avila v. Bondi", ...)` (`query_id: dca7c886`) -> 1 result: *Joaquin Avila v. Pamela Bondi*, No. 25-3248 (8th Cir. Mar. 25, 2026), cluster `10814776`, opinion `11281530`.
13. `mcp_courtlistener_search(type="o", citation="175 F.4th 61", ...)` (`query_id: c8a1f3f2`) -> 0 results.
14. `mcp_courtlistener_read_document(opinion_id=11415407, chunk_index=[7,8,9,10,11,12,13], chunk_size=8000)` -> read First Circuit structural, surplusage (§ 1226(c)(1)(E) / Laken Riley Act), *Jennings*, *Preap*, *Al Otro Lado*, and 30-year executive-practice analysis.
15. `mcp_courtlistener_read_document(opinion_id=11281530, chunk_index=[0,1,2,3], chunk_size=8000)` -> read Eighth Circuit's pro-government opinion in *Avila v. Bondi*.
16. `mcp_courtlistener_read_document(opinion_id=11415407, chunk_index=[1,2], chunk_size=8000)` -> re-read full procedural history and footnote 5 confirming the government did not appeal class certification.

## 3. Domain-Scoped Government Web Lookups (`google_web_search` / `web_fetch`)

1. `google_web_search`: `site:justice.gov "Guerrero Orellana" OR "26-630" OR "Barbosa da Cunha" OR "26-104"` -> confirmed both *Rhoney v. Barbosa da Cunha* (No. 26-104, cert granted Oct. 1, 2026) and *Mullin v. Guerrero Orellana* (No. 26-630, docketed Nov. 13, 2026) are Solicitor General petitions on 8 U.S.C. § 1225(b)(2)(A) vs. § 1226(a).
2. `google_web_search`: `site:supremecourt.gov "26-630" OR "26-104" "Barbosa da Cunha"` -> returned docket summaries for No. 26-104 and No. 26-630.
3. `web_fetch`: `https://www.supremecourt.gov/docket/docketfiles/html/public/26-630.html` and `https://www.supremecourt.gov/docket/docketfiles/html/public/26-104.html` -> retrieved official docket proceedings for No. 26-630 (showing Nov. 19, 2026 Respondent waiver of right to respond) and No. 26-104 (showing Oct. 1, 2026 grant and merits briefing schedule).
4. `google_web_search`: `site:justice.gov "Guerrero Orellana" "26-104" OR "hold" OR "petition for a writ of certiorari"` -> confirmed the SG's petition in No. 26-630 requests a hold pending *Rhoney v. Barbosa da Cunha*, No. 26-104.
5. `web_fetch`: `https://www.supremecourt.gov/docket/QP/26-00104qp.pdf` -> failed with HTTP 404 Not Found (no electronic QP PDF posted on Rule 34.6 paper-only docket).
6. `google_web_search`: `site:supremecourt.gov "Cirrus Rojas" OR "Rodriguez Vazquez" OR "Lopez-Campos" OR "Santillan Quiroz" OR "Hernandez Alvarez"` -> identified sister SG § 1225(b)(2)(A) hold petitions (`25-1415`, `26-568`, `26-572`).

## 4. Committed Repository Base-Rate & Schema Files Consulted

- `metrics/statpack.md`, `metrics/statpack.json` (`sal-v9` `alt_segments` verification), `metrics/README.md`, `docs/salience.md`, `docs/outcome-decomposition.md`, and `src/fedcourtsai/pipeline/claims.py` (claim ID and resolution semantics verification).
