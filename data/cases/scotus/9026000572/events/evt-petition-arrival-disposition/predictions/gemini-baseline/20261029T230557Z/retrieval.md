# Retrieval Log: `scotus/9026000572` (`evt-petition-arrival-disposition`)

Mode: `forward` (`decided_before: null`).

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent OT2026 SCOTUS grants, including `scotus/9026000104`, *Philip L. Rhoney, Acting Director of the Buffalo Field Office of U.S. Immigration and Customs Enforcement v. Ricardo Aparecido Barbosa da Cunha* (No. 26-104, certiorari granted October 1, 2026, originating from CA2 No. 25-3141).

2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 34 GET(s), 8847360 byte(s)`
   - Result: Returned 10 recent OT2026 SCOTUS GVR dispositions (including `scotus/9026000048`, *Mullin v. National TPS Alliance*, No. 26-48).

3. `uv run fedcourts query --court scotus --docket-number 26-104`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned `scotus/9026000104` (*Rhoney v. Barbosa da Cunha*, No. 26-104, cert granted Oct. 1, 2026).

4. `uv run fedcourts query --court scotus --docket-number 25-1415`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/73529868` (*Matthew Putra, Director of the Detroit Field Office of U.S. Immigration and Customs Enforcement, et al. v. Juan Manuel Lopez-Campos, et al.*, No. 25-1415, distributed for conference Sept. 28, 2026, open/held).

5. `uv run fedcourts query --court scotus --docket-number 26-43`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/9026000043` (*Victor Buenrostro-Mendez, et al. v. Todd Blanche, Attorney General, et al.*, No. 26-43, distributed for conference Sept. 28, 2026, open/held).

6. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 30`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 30 recent 2020s SCOTUS rows.

7. `uv run fedcourts query --court scotus --attorney "D. John Sauer" --include-open --limit 30`
   - Transfer line: none (failed with exit code 2: `No such option: --attorney`).

8. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 200 | grep -i -E "Field Office|Casta|Hernandez|Santillan|Avila|Barbosa|Lopez-Campos|Buenrostro"`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)` (printed to stderr/stdout before pipe; grep exited 1 with no matching lines in the top 200 date-ordered rows).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `court="ca7"`, `docket_number="25-3127"`)
   - Result: Returned 2 opinion clusters in *Jaciel Rojas v. Samuel Olson*, No. 25-3127 (7th Cir.): an April 3, 2026 interim order (`cluster_id: 10936834`) and the July 30, 2026 merits decision (`cluster_id: 11056777`, `opinion_id: 11404410`, authored by Judge Kolar, dissent by Judge Sykes).

2. `mcp_courtlistener_search` (`type="r"`, `court="ca7"`, `docket_number="25-3127"`)
   - Result: Returned RECAP docket `71965444` (*Jaciel Rojas v. Samuel Olson*, No. 25-3127).

3. `mcp_courtlistener_read_document` (`opinion_id=11404410`, `chunk_index=[0, 1, 2, 3]`)
   - Result: Read chunks 0–3 of the Seventh Circuit's July 30, 2026 opinion in *Jaciel Rojas v. Samuel Olson*, No. 25-3127 (covering background, mootness holding, statutory framework, and footnote 1 cataloging the 5–2 circuit split and pending cert petitions including No. 26-104, No. 25-1415, and No. 26-43).

4. `mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `docket_number="25-3141"`)
   - Result: Returned 2 opinion clusters in *Barbosa Da Cunha v. Freden*, 175 F.4th 61 (2d Cir. May 15, 2026) (`cluster_id: 10983473` and amended opinion `cluster_id: 11022036` filed June 29, 2026).

5. `mcp_courtlistener_read_document` (`opinion_id=11404410`, `chunk_index=[8, 9, 10, 11, 12]`)
   - Result: Read chunks 8–12 of the Seventh Circuit's July 30, 2026 opinion in *Rojas v. Olson*, covering the conclusion of the majority opinion and the entirety of Judge Sykes's dissent (including page 56 & n.1 noting the pending Solicitor General cert petitions in *Rhoney v. Barbosa da Cunha*, No. 26-104, and *Raycraft v. Lopez-Campos*, No. 25-1415, and the detainees' petition in *Buenrostro-Mendez v. Blanche*, No. 26-43).

6. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `q=""Barbosa da Cunha" OR "Lopez-Campos" OR "Buenrostro-Mendez" OR "Santillan Quiroz" OR "Hernandez Alvarez""`)
   - Result: 0 results (expected given thin SCOTUS docket coverage on CourtListener search).

7. `mcp_courtlistener_read_document` (`opinion_id=11404410`, `chunk_index=[4, 5, 6, 7]`)
   - Result: Read chunks 4–7 of the Seventh Circuit's July 30, 2026 opinion in *Rojas v. Olson*, completing the full read of all 13 chunks (`100,992` chars) of the opinion below.

## 3. Web Searches (`google_web_search`)

1. `google_web_search` (`query=""Rhoney v. Barbosa da Cunha" OR "Barbosa da Cunha" "26-104" OR "Padula v. Rojas""`)
   - Result: No search results returned.
