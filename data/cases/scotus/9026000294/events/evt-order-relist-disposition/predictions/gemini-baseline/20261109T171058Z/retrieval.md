# Retrieval Log

## 1. Corpus Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000294" --event "evt-order-relist-disposition" --role predictor`
   - Resolved case (`scotus/9026000294`), corpus (`corpus/corpus.db`), and event (`data/cases/scotus/9026000294/events/evt-order-relist-disposition/event.yaml`) paths.
2. `uv run fedcourts query --help`
   - Inspected available structured filter flags for `fedcourts query`.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
   - Returned 10 recent 2020s SCOTUS granted rows (OT 2026 cert grants and substantive interim grants) with distribution counts, counsel, and amicus metadata.
4. `uv run fedcourts query --court scotus --docket-number 26-292`
   - Transfer line: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Returned the corpus row for companion *vide* petition *Fiona Havlish, et al. v. The Taliban, et al.* (`scotus/9026000292`, `distribution_count: 2`, amicus briefs by Naseer A. Faiq and by Iowa and 30 other States).
5. `uv run fedcourts query --court scotus --docket-number 26-293`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned the corpus row for companion *vide* petition *Kathleen Ashton, et al. v. The Taliban, et al.* (`scotus/9026000293`, `distribution_count: 2`, amicus brief by Naseer A. Faiq).
6. `uv run fedcourts query --court scotus --originating-court ca2 --era 2020s --disposition granted --limit 10`
   - Failed with usage error (`No such option: --originating-court`).
7. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent OT 2026 denied cert petitions (resolved 2026-11-09), including several denied after `distribution_count: 2` (1 relist).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca2", case_name="Havlish v. Taliban", fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Returned 2 clusters on consolidated docket `23-258(L); 23-354(L)`:
     - `cluster_id: 10660852` (`opinion_id: 11127439`, filed `2025-08-26`, *Havlish v. Taliban; Aliganga v. Taliban*, 152 F.4th 339 (2d Cir. 2025)).
     - `cluster_id: 10802300` (`opinion_id: 11277807`, filed `2026-03-19`, order denying rehearing en banc and accompanying concurrences and dissents, 170 F.4th 100 (2d Cir. 2026)).
2. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[0, 1, 2, 3], chunk_size=8000)`
   - Read chunks 0–3 of the Second Circuit panel opinion (`152 F.4th 339`), covering the background of the DAB reserves at the FRBNY, the procedural history of the Judgment Plaintiffs (*Havlish*/*Ashton*) and Pre-Judgment Plaintiffs (*Owens*), and the beginning of the *sua sponte* immunity analysis.
3. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0, 1, 2, 3, 4], chunk_size=8000)`
   - Read chunks 0–4 of the Second Circuit en banc denial order (`170 F.4th 100`), covering Judge Nardini's concurrence in denial of rehearing en banc, Judge Sullivan's dissent (joined by Chief Judge Livingston and Judges Bianco and Park) on FSIA and TRIA, and the beginning of Judge Menashi's separate dissent.
4. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[5, 6, 7, 8, 9, 10], chunk_size=8000)`
   - Read chunks 5–10 (the remainder) of `opinion_id: 11277807`, covering Judge Menashi's defense of *Zivotofsky* executive recognition on § 1603(a), his dissent on § 1603(b)(2) instrumentality ownership and TRIA timing, and Judges Cabranes and Calabresi's statement respecting the denial of rehearing en banc.
5. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[4, 5, 6, 7, 8, 9, 10], chunk_size=8000)`
   - Read chunks 4–10 of `opinion_id: 11127439`, covering the panel's unanimous holding on *sua sponte* recognition of FSIA execution immunity (`28 U.S.C. §§ 1609, 1611(b)(1)`), its holding that Afghanistan is a recognized foreign state and DAB is its agency or instrumentality under the 2003 Afghanistan Bank Law (including footnote 97 disclaiming deference to the Executive on § 1603(b)), and its holding that TRIA § 201(a) abrogates FSIA immunity.
6. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[11, 12, 13], chunk_size=8000)`
   - Read chunks 11–13 of `opinion_id: 11127439`, covering the panel's TRIA agency-or-instrumentality timing holding and the opening of Judge Sullivan's partial concurrence and partial dissent.

## 3. Web Searches

None attempted.
