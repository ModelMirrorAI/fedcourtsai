# Retrieval Log (`scotus/9026000292` / `evt-order-cvsg-disposition`)

Mode: `forward` (`record/context.json`: `"mode": "forward"`, `"cutoff": "2026-11-17"`). All external retrievals targeted case filings, companion docket framing, lower-court and Supreme Court opinions, and official Executive Branch orders; no external forecasts or predictions were sought or encountered.

## 1. Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000292" --event "evt-order-cvsg-disposition" --role predictor` and `uv run fedcourts query --help`
   - Resolved case/event paths and inspected structured filter options (no ranged corpus transfer).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - `ranged corpus reads: 40 GET(s), 10420224 byte(s)`
   - Returned 10 recent OT 2026 granted SCOTUS rows (including post-CVSG grant *Robinhood Markets, Inc. v. Sodha*, No. 25-944, confirming post-CVSG conference distribution increments, and Solicitor General D. John Sauer filings).
3. `uv run fedcourts query --citation "578 U.S. 212" --limit 5`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows with coverage note (`only 195 row(s) in scope (any court) carry any reporter citation at all` — lookup for *Bank Markazi v. Peterson*).
4. `uv run fedcourts query --citation "583 U.S. 202" --limit 5`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 0 rows with the same sparse-citation coverage note (lookup for *Rubin v. Islamic Republic of Iran*).
5. `uv run fedcourts query --court scotus --originating-court ca2 --era 2020s --disposition granted --limit 15`
   - Failed with CLI usage error (`Exit Code: 2`, `No such option: --originating-court`).
6. `uv run fedcourts query --court scotus --docket-number 26-293 --include-open`
   - `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Returned open companion docket `scotus/9026000293` (*Kathleen Ashton, et al. v. The Taliban, et al.*, `cvsg_date: "2026-11-16"`, `distribution_count: 2`, `salience_score: 0.3058`).
7. `uv run fedcourts query --court scotus --docket-number 26-294 --include-open`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned open companion docket `scotus/9026000294` (*James Owens, et al. v. The Taliban, et al.*, `cvsg_date: "2026-11-16"`, `distribution_count: 2`, `salience_score: 0.3058`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="152 F.4th 339", fields=["caseName","citation","cluster_id","dateFiled","docketNumber","opinions"])`
   - Returned 0 results (`query_id: 7dc342d5`; recent F.4th reporter pagination not yet indexed in citation search).
2. `mcp_courtlistener_search(type="o", citation="170 F.4th 100", fields=["caseName","citation","cluster_id","dateFiled","docketNumber","opinions"])`
   - Returned 0 results (`query_id: aaa01735`).
3. `mcp_courtlistener_search(type="o", case_name="Havlish", court="ca2", filed_after="2025-01-01", fields=["caseName","citation","cluster_id","dateFiled","docketNumber","opinions"])`
   - Returned 2 results (`query_id: de2ec893`): `cluster_id=10660852` / `opinion_id=11127439` (Aug. 26, 2025 Second Circuit panel opinion and dissent) and `cluster_id=10811059` / `opinion_id=11277807` (Mar. 19, 2026 Second Circuit order denying rehearing en banc, concurrences, and dissents).
4. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[4,5,6,7,8,9,10], chunk_size=8000)`
   - Read FSIA sovereign-recognition and instrumentality portions of the Aug. 26, 2025 Second Circuit panel opinion.
5. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0,1,2,3,4,5,6,7], chunk_size=8000)`
   - Read chunks 0–7 of the Mar. 19, 2026 Second Circuit rehearing en banc order and separate writings (partially truncated in tool display; re-read in smaller chunks below).
6. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[11,12,13,14,15,16,17,18,19], chunk_size=8000)`
   - Read chunks 11–19 of `opinion_id=11127439` covering the panel's TRIA blocking-date holding and Judge Sullivan's dissent (partially truncated in tool display; re-read in smaller chunks below).
7. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[8,9,10], chunk_size=8000)`
   - Read Judge Menashi's en banc dissent on TRIA § 201(a) and Judges Cabranes and Calabresi's joint statement.
8. `mcp_courtlistener_search(type="o", case_name="CIMEX", court="scotus", filed_after="2025-01-01", fields=["caseName","citation","cluster_id","dateFiled","docketNumber","opinions"])`
   - Returned 1 result (`query_id: bb012c5a`): *Exxon Mobil Corp. v. Corporación Cimex, S.A. (Cuba)* (`cluster_id=10878556`, `opinion_id=11346053`, decided June 23, 2026).
9. `mcp_courtlistener_search(type="o", citation="771 F.3d 713", fields=["caseName","citation","cluster_id","dateFiled","opinions"])`
   - Returned 2 results (`query_id: 04987018`), locating *Stansell v. Revolutionary Armed Forces of Colombia (FARC)* (`opinion_id=2742884`, 11th Cir. 2014).
10. `mcp_courtlistener_search(type="o", citation="825 F.3d 949", fields=["caseName","citation","cluster_id","dateFiled","opinions"])`
    - Returned 2 results (`query_id: 99f04dbb`), locating *Bennett v. Islamic Republic of Iran* (`opinion_id=8414040`, 9th Cir. 2016).
11. `mcp_courtlistener_read_document(opinion_id=11346053, chunk_index=[0,1], chunk_size=8000)`
    - Read syllabus and opening background of *Exxon Mobil Corp. v. Corporación Cimex, S.A.* (June 23, 2026).
12. `mcp_courtlistener_search_document(opinion_id=2742884, query="instrumentality")`
    - Returned 55 matches (20 shown) in *Stansell II*, examining how the Eleventh Circuit analyzed TRIA instrumentality status.
13. `mcp_courtlistener_search_document(opinion_id=8414040, query="instrumentality")`
    - Returned 29 matches (20 shown) in *Bennett*, confirming Bank Melli's continuous Iranian state ownership before and after blocking.
14. `mcp_courtlistener_search_document(opinion_id=2742884, query="was ever")`
    - Returned 1 match in *Stansell II* addressing the district court's temporal formulation.
15. `mcp_courtlistener_search_document(opinion_id=8414040, query="blocked")`
    - Returned 25 matches (20 shown) in *Bennett* on TRIA blocked-asset attachment.
16. `mcp_courtlistener_search(type="o", citation="45 F.4th 1340", fields=["caseName","citation","cluster_id","dateFiled","opinions"])`
    - Returned 0 results (`query_id: c24f0d69`; F.4th reporter citation for *Stansell III* not indexed in citation field).
17. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0,1,2,3], chunk_size=7000)`
    - Read complete text of Judge Nardini's concurrence in denial of rehearing en banc and the first half of Judge Sullivan's 4-judge dissent from denial of rehearing en banc.
18. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[4,5,6,7], chunk_size=7000)`
    - Read remainder of Judge Sullivan's en banc dissent and the first part of Judge Menashi's en banc dissent.
19. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[13,14,15], chunk_size=7000)`
    - Read complete text of the Second Circuit panel majority's TRIA "blocking-date" holding and the opening of Judge Sullivan's panel dissent (omitted from `petition.txt` at the 150k-character cap).
20. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[16,17,18,19], chunk_size=7000)`
    - Read remainder of Judge Sullivan's panel dissent in `152 F.4th 339`.

## 3. Web Fetch and Web Search Calls (`forward` mode)

1. `web_fetch` on the three unstaged Supreme Court filings linked in `snapshots/2026-11-16.json`:
   - `https://www.supremecourt.gov/DocketPDF/26/26-292/431386/20261030172431937_26-292_Motion%20and%20Supplemental%20Brief.pdf` (Petitioners' Oct. 30, 2026 Motion for Leave and Supplemental Brief responding to amicus Faiq)
   - `https://www.supremecourt.gov/DocketPDF/26/26-292/428411/20261005114322425_10.02%20-%20DRAFT%20-%20Havlish%20v.%20Taliban%20Amicus.pdf` (Oct. 5, 2026 Brief of Iowa and 30 Other States as Amici Curiae in Support of Petitioners)
   - `https://www.supremecourt.gov/DocketPDF/26/26-292/428536/20261005173612123_Faiq%20cert%20op%20%20-%20final%20to%20printer.pdf` (Oct. 5, 2026 Brief of Chargé d'Affaires Naseer A. Faiq as Amicus Curiae in Opposition to Certiorari)
   - Extracted summaries of all three filings' exact arguments (confirming Faiq served as the sole adversarial opposition at the cert stage and explaining why Petitioners sought leave to file a supplemental brief in lieu of a Rule 15.6 reply).
2. `google_web_search(query='"26-293" "Ashton" "Taliban" OR "26-294" "Owens" "Taliban" site:supremecourt.gov')`
   - Confirmed the Questions Presented across companion dockets No. 26-293 (*Ashton*, TRIA blocking-date question + *CIMEX* framing) and No. 26-294 (*Owens*, pre-judgment FSIA attachment, sovereign recognition, and § 1611(b)(1) central-bank immunity questions). No forecasts surfaced.
3. `google_web_search(query='"Executive Order 14064" ("2025" OR "2026") continuation national emergency Afghanistan')`
   - Confirmed White House / Federal Register notices continuing Executive Order 14064's national emergency with respect to Afghanistan and DAB reserves on February 7, 2025 (`90 Fed. Reg. 9279`) and February 9, 2026 (`91 Fed. Reg. 5941`). No forecasts surfaced.
