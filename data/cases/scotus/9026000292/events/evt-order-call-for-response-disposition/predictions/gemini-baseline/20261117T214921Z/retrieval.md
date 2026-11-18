# Retrieval Log

Mode: `forward` (`DECIDED_BEFORE` unset; `context.decided_before: null`). No web searches were attempted, and no post-decision or third-party forecast material was sought or encountered.

## 1. Corpus CLI (`fedcourts`) Calls

1. **Path resolution & CLI help (local metadata only, no corpus reads):**
   - Command: `uv run fedcourts paths --court "scotus" --docket "9026000292" --event "evt-order-call-for-response-disposition" --role predictor` and `uv run fedcourts query --help`
   - Result: Confirmed `case_id` (`scotus/9026000292`), `event.yaml` path, and valid `fedcourts query` filter flags (no transfer line printed).

2. **SCOTUS precedents cited in petition (by reporter citation):**
   - Command: `uv run fedcourts query --court scotus --citation "146 S. Ct. 1909" --citation "145 S. Ct. 2090" --citation "578 U.S. 212" --citation "583 U.S. 202" --citation "538 U.S. 468" --limit 10`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: 0 rows returned (`note:` explained only 195 SCOTUS rows carry reporter citations in the `citations` column).

3. **Recent 2020s granted SCOTUS cases (priors):**
   - Command: `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
   - Result: 10 rows returned (recent OT2025/OT2026 grants, including `25-944` *Robinhood Markets, Inc. v. Sodha* granted post-CVSG after 3 distributions, `26-239`, `26A560`, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`).

4. **Attempted originating-court filter (grants) — failed CLI flag:**
   - Command: `uv run fedcourts query --court scotus --originating-court ca2 --era 2020s --disposition granted --limit 15`
   - Transfer line: none (exit code 2: `No such option: --originating-court`).

5. **Attempted originating-court filter (denials) — failed CLI flag:**
   - Command: `uv run fedcourts query --court scotus --originating-court ca2 --era 2020s --disposition denied --limit 10`
   - Transfer line: none (exit code 2: `No such option: --originating-court`).

6. **Recent 2020s denied SCOTUS cases (priors):**
   - Command: `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 5 rows returned from warm cache (`25-1238` *Mizrahi v. United States* from CA2, `25-1240`, `25-1303`, `25-1324`, `25-7485`).

7. **Recent 2020s GVR SCOTUS cases (priors):**
   - Command: `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 5 rows returned from warm cache (`25-1421`, `26-5528`, `25-442` *Roybal v. Griffith* GVR'd post-CVSG after 3 distributions, `25-1348`, `26-5123`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", citation="152 F.4th 339", fields=["caseName","citation","dateFiled","court_id","cluster_id","docketNumber","opinions"])`
   - Result: `count: 0` (`query_id: 6026146a`; recent Federal Reporter 4th cite not yet indexed in citation array).
2. `mcp_courtlistener_search(type="o", citation="170 F.4th 100", fields=["caseName","citation","dateFiled","court_id","cluster_id","docketNumber","opinions"])`
   - Result: `count: 0` (`query_id: 80290033`).
3. `mcp_courtlistener_search(type="o", court="ca2", docket_number="23-258", fields=["caseName","citation","dateFiled","court_id","cluster_id","docketNumber","opinions"])`
   - Result: `count: 2` (`query_id: a4db11d4`). Located both decisions below in *Havlish v. Taliban; Aliganga v. Taliban*: the August 26, 2025 panel decision (`cluster_id: 10660852`, `opinion_id: 11127439`) and the March 19, 2026 order denying rehearing en banc (`cluster_id: 10862000`, `opinion_id: 11277807`).
4. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[5,6,7,8,9,10,11], chunk_size=8000)`
   - Result: Read chunks 5–11 of `11127439` (156,644 total chars), covering Judge Cabranes's *Zivotofsky* recognition-power analysis and the start of the TRIA § 201(a) analysis omitted from `petition.txt`.
5. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0,1,2,3,4,5,6,7,8], chunk_size=8000)`
   - Result: Read chunks 0–8 of `11277807` (82,791 total chars), covering the en banc denial order and separate opinions.
6. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[12,13,14,15,16,17,18,19], chunk_size=8000)`
   - Result: Read chunks 12–19 of `11127439`, covering the panel majority's distinction of *Kirschenbaum*, *Bennett*, and *Stansell III*, its "at-the-time-of-blocking" holding, and Judge Sullivan's full panel dissent.
7. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[8,9,10], chunk_size=8000)`
   - Result: Read chunks 8–10 of `11277807`, covering the conclusion of Judge Menashi's en banc dissent and Judges Cabranes and Calabresi's statement respecting the denial of rehearing en banc.
8. `mcp_courtlistener_search(type="o", court="scotus", case_name="Havana Docks", fields=["caseName","citation","dateFiled","cluster_id","opinions"])`
   - Result: `count: 1` (`query_id: fe6de84d`). Located *Havana Docks Corp. v. Royal Caribbean Cruises, Ltd.* (`cluster_id: 10862763`, `opinion_id: 11330193`, filed `2026-03-23`).
9. `mcp_courtlistener_search(type="o", citation="45 F.4th 1340", fields=["caseName","citation","dateFiled","cluster_id","opinions"])`
   - Result: `count: 0` (`query_id: 60c2b0d9`).
10. `mcp_courtlistener_search(type="o", citation="825 F.3d 949", fields=["caseName","citation","dateFiled","cluster_id","opinions"])`
    - Result: `count: 2` (`query_id: 59f1daa7`), locating *Bennett v. Islamic Republic of Iran* (`cluster_id: 3212767`, `opinion_id: 8414040` and `8414041`, 9th Cir. 2016).
11. `mcp_courtlistener_search(type="o", court="ca11", case_name="Stansell", fields=["caseName","citation","dateFiled","cluster_id","opinions"])`
    - Result: `count: 5` (`query_id: c01a3024`), locating *Keith Stansell v. UBS Financial Services, Inc.* (`45 F.4th 1340`, `cluster_id: 7374255`, `opinion_id: 7802935`, filed `2022-08-23`).
12. `mcp_courtlistener_read_document(opinion_id=11330193, chunk_index=0, chunk_size=6000)`
    - Result: Read syllabus of *Havana Docks* (`11330193`, 75,811 total chars).
13. `mcp_courtlistener_search_document(opinion_id=8414040, query="instrumentality", snippet_size=400)`
    - Result: 29 matches (20 shown) in *Bennett* (`8414040`).
14. `mcp_courtlistener_search_document(opinion_id=7802935, query="time of", snippet_size=400)`
    - Result: 2 matches in *Stansell III* (`7802935`).
15. `mcp_courtlistener_search_document(opinion_id=8414040, query="at the time", snippet_size=400)`
    - Result: 1 match in *Bennett* (`8414040`).
16. `mcp_courtlistener_search_document(opinion_id=7802935, query="was or is", snippet_size=500)`
    - Result: 0 matches in *Stansell III* (`7802935`).
17. `mcp_courtlistener_search_document(opinion_id=8414040, query="currently", snippet_size=500)`
    - Result: 1 match in *Bennett* (`8414040`).
18. `mcp_courtlistener_search_document(opinion_id=7802935, query="writ", snippet_size=500)`
    - Result: 13 matches in *Stansell III* (`7802935`), locating the TRIA agency/instrumentality timing discussion at chunk 3.
19. `mcp_courtlistener_read_document(opinion_id=7802935, chunk_index=3, chunk_size=8000)`
    - Result: Read chunk 3 of *Stansell III* (`7802935`), verifying the Eleventh Circuit's exact holding on TRIA § 201(a) timing.
20. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0,1,2,3,4], chunk_size=6000)`
    - Result: Read full text of Judge Nardini's concurrence in the denial of rehearing en banc and the opening of Judge Sullivan's en banc dissent.
21. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[5,6,7], chunk_size=6000)`
    - Result: Read Part III of Judge Sullivan's en banc dissent and the opening of Judge Menashi's en banc dissent.

## 3. Web Searches

None attempted.
