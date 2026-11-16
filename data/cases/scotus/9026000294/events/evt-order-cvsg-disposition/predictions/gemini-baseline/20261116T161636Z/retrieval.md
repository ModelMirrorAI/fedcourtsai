# Retrieval Log

Mode: `forward` (`DECIDED_BEFORE` unset).

## Corpus CLI (`uv run fedcourts ...`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000294" --event "evt-order-cvsg-disposition" --role predictor` and `uv run fedcourts query --help`
   - Transfer: none (path resolution and CLI help).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 40 GET(s), 10420224 byte(s)`
   - Returned 10 recent OT2026 granted priors, including post-CVSG grant *Robinhood Markets, Inc. v. Sodha* (No. 25-944).
3. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1909" --citation "604 U.S. 115" --citation "598 U.S. 264" --limit 5`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows with sparse-citation coverage note (`only 195 row(s) in scope (scotus) carry any reporter citation at all`).
4. `uv run fedcourts query --court scotus --docket-number 26-292`
   - Transfer: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Returned 1 row: companion *Fiona Havlish, et al. v. The Taliban, et al.* (No. 26-292).
5. `uv run fedcourts query --court scotus --docket-number 26-293`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm corpus service cache)
   - Returned 1 row: companion *Kathleen Ashton, et al. v. The Taliban, et al.* (No. 26-293).
6. `uv run fedcourts query --court scotus --docket-number 22-859`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: *SEC v. Jarkesy* (No. 22-859; checked while looking up prior FSIA docket numbers).
7. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Returned 10 rows of recent OT2026 cert denials (November 16, 2026 order list).
8. `uv run fedcourts query --court scotus --attorney "D. John Sauer" --era 2020s --disposition denied --limit 15`
   - Failed with CLI usage error (`No such option: --attorney`, exit code 2; no corpus transfer).
9. `uv run fedcourts query --court scotus --docket-number 24-699`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: *Exxon Mobil Corporation v. Corporación Cimex, S.A. (Cuba), et al.* (No. 24-699; CVSG `2025-05-05`, granted `2025-10-03`, reversed `2026-06-23`).
10. `uv run fedcourts query --court scotus --docket-number 23-160`
    - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned 1 row: *Mora v. United States* (No. 23-160; checked while looking up *OI European Group* cert docket).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca2", case_name="Havlish v. Taliban")`
   - Returned 2 Second Circuit opinion clusters: panel decision filed `2025-08-26` (`cluster_id: 10660852`, `opinion_id: 11127439`) and order/opinions denying rehearing en banc filed `2026-03-19` (`cluster_id: 10838478`, `opinion_id: 11277807`).
2. `mcp_courtlistener_search(type="o", citation="152 F.4th 339")`
   - Returned 0 results (reporter citation not yet attached to cluster in search index).
3. `mcp_courtlistener_search(type="o", citation="170 F.4th 100")`
   - Returned 0 results (reporter citation not yet attached to cluster in search index).
4. `mcp_courtlistener_search(type="o", court="scotus", case_name="Exxon Mobil v. Corporacion Cimex")`
   - Returned 0 results (diacritic/caption mismatch on `case_name` filter).
5. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0, 1, 2, 3, 4], chunk_size=12000)`
   - Read chunks 0–4 of 7 of the Second Circuit en banc denial order and opinions (Nardini concurrence, Sullivan dissent, start of Menashi dissent).
6. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[0, 1, 2, 3, 4], chunk_size=12000)`
   - Read chunks 0–4 of 14 of the Second Circuit panel opinion (Cabranes, J., background, TRIA holding, and start of FSIA holding).
7. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[5, 6], chunk_size=12000)`
   - Read remaining chunks 5–6 of 7 of the Second Circuit en banc denial opinions (remainder of Menashi dissent and Cabranes/Calabresi statement).
8. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[5, 6, 7, 8, 9, 10, 11, 12, 13], chunk_size=12000)`
   - Read remaining chunks 5–13 of 14 of the Second Circuit panel decision (FSIA § 1603(b)(2) holding including Footnote 97 and Judge Sullivan's panel dissent).
9. `mcp_courtlistener_search(type="o", court="scotus", q='"Cimex" "Foreign Sovereign Immunities Act"')`
   - Returned 1 result: *Exxon Mobil Corp. v. Corporación Cimex, S. A. (Cuba)*, No. 24-699 (`cluster_id: 10878536`, `opinion_id: 11346053`, decided `2026-06-23`).
10. `mcp_courtlistener_read_document(opinion_id=11346053, chunk_index=0, chunk_size=10000)`
    - Read chunk 0 (Syllabus) of *Exxon Mobil Corp. v. Corporación Cimex, S. A. (Cuba)*.
11. `mcp_courtlistener_search(type="o", case_name="OI European Group")`
    - Returned 2 results: *OI European Group BV v. Bolivarian Republic of Venezuela*, `73 F.4th 157` (3d Cir. 2023), and the underlying D.D.C. opinion.

## Web Searches

None attempted.
