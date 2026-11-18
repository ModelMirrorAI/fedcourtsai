# Retrieval Log — `scotus/9026000294` (`evt-order-call-for-response-disposition`, `20261117T214921Z`)

## 1. Corpus CLI Queries (`fedcourts query`)

1. **Citation lookup for Supreme Court FSIA precedents cited in the petition**
   - Command: `uv run fedcourts query --court scotus --citation "560 U.S. 305" --citation "541 U.S. 677" --citation "598 U.S. 264" --citation "604 U.S. 115" --citation "146 S. Ct. 1909" --limit 10`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Output: Returned 0 rows, with CLI note explaining that only 195 `scotus` rows carry reporter citations in the `citations` column (which stores a case's own parallel cites rather than a citation-network graph).

2. **Recent 2020s granted SCOTUS priors**
   - Command: `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Output: Returned 10 granted 2020s SCOTUS rows, including CVSG grant `scotus/73280982` (*Robinhood Markets, Inc. v. Sodha*, No. 25-944, `cvsg_date: 2026-06-01`, `distribution_count: 3`), cert grants `26-239`, `25-1408`, `26-12`, `26-204`, `25-1103`, `25-7026`, and substantive applications `26A560`, `26A512`, `26A476`.

## 2. CourtListener MCP Lookups

*(Used because `decision-below.txt` was absent from `record/documents/` due to the Second Circuit docketing its combined opinions on lead consolidated docket No. 23-258 rather than member docket No. 23-354.)*

1. **`mcp_courtlistener_search` (opinion search by citation `152 F.4th 339`)**
   - Parameters: `type="o", citation="152 F.4th 339", fields=["id", "cluster_id", "caseName", "citation", "court_id", "dateFiled", "docketNumber", "judge", "opinions"]`
   - Result: `query_id: 744703ea`, `count: 0` (F.4th reporter pagination not yet populated on the cluster record).

2. **`mcp_courtlistener_search` (opinion search by citation `170 F.4th 100`)**
   - Parameters: `type="o", citation="170 F.4th 100", fields=["id", "cluster_id", "caseName", "citation", "court_id", "dateFiled", "docketNumber", "judge", "opinions"]`
   - Result: `query_id: 0082aaa4`, `count: 0`.

3. **`mcp_courtlistener_search` (opinion search by case name `Havlish v. Taliban` in `ca2`)**
   - Parameters: `type="o", case_name="Havlish v. Taliban", court="ca2", fields=["id", "cluster_id", "caseName", "citation", "court_id", "dateFiled", "docketNumber", "judge", "opinions"]`
   - Result: `query_id: c1a90dc7`, `count: 2` — matched both Second Circuit combined decisions in *Havlish v. Taliban; Aliganga v. Taliban*, Nos. `23-258 (L); 23-354 (L)`: cluster `10660852` / `opinion_id: 11127439` (filed `2025-08-26`) and cluster `10851225` / `opinion_id: 11277807` (filed `2026-03-19`).

4. **`mcp_courtlistener_read_document` (panel opinion, chunks 0–3)**
   - Parameters: `opinion_id=11127439, chunk_index=[0, 1, 2, 3], chunk_size=8000`
   - Result: Read chunks 0–3 of 20 (`total_chars: 156644`) — full caption (showing Federal Reserve Bank of New York as Garnishee-Interested-Party-Appellee), procedural history, and Section II.A (*sua sponte* attachment immunity review).

5. **`mcp_courtlistener_read_document` (en banc denial order, chunks 0–3)**
   - Parameters: `opinion_id=11277807, chunk_index=[0, 1, 2, 3], chunk_size=8000`
   - Result: Read chunks 0–3 of 11 (`total_chars: 82791`) — 13-judge active lineup, en banc denial order, Judge Nardini concurrence (joined by Judge Lohier), and Judge Sullivan dissent (joined by Chief Judge Livingston and Judges Bianco and Park).

6. **`mcp_courtlistener_read_document` (panel opinion, chunks 4–9)**
   - Parameters: `opinion_id=11127439, chunk_index=[4, 5, 6, 7, 8, 9], chunk_size=8000`
   - Result: Read chunks 4–9 of 20 — panel majority's FSIA analysis holding that Executive recognition of Afghanistan is conclusive under *Zivotofsky* and that Da Afghanistan Bank is an agency or instrumentality of Afghanistan under 28 U.S.C. § 1603(b), plus start of TRIA discussion.

7. **`mcp_courtlistener_read_document` (en banc denial order, chunks 4–10)**
   - Parameters: `opinion_id=11277807, chunk_index=[4, 5, 6, 7, 8, 9, 10], chunk_size=8000`
   - Result: Read chunks 4–10 of 11 — conclusion of Judge Sullivan's dissent, full text of Judge Menashi's separate dissent (agreeing with presidential recognition of Afghanistan under *Zivotofsky* while dissenting on FSIA § 1603(b) and TRIA § 201(a)), and statement of Judges Cabranes and Calabresi.

8. **`mcp_courtlistener_read_document` (panel opinion & dissent, chunks 13–19)**
   - Parameters: `opinion_id=11127439, chunk_index=[13, 14, 15, 16, 17, 18, 19], chunk_size=8000`
   - Result: Read chunks 13–19 of 20 — panel majority's 8-point holding summary and full text of Judge Sullivan's panel opinion concurring in part and dissenting in part.

## 3. Official Docket Lookups (`web_fetch` in `forward` mode)

1. **`web_fetch` on companion `supremecourt.gov` docket pages (`26-292` and `26-293`)**
   - URLs fetched: `https://www.supremecourt.gov/docket/docketfiles/html/public/26-292.html` and `https://www.supremecourt.gov/docket/docketfiles/html/public/26-293.html`
   - Result: Confirmed counsel blocks omitted from the stripped `record/related/*.json` summaries: Stuart H. Singer (Boies Schiller Flexner LLP) for petitioners in No. 26-292 (*Havlish*) alongside an amicus brief of Iowa and 30 other States (Eric Harris Wessan), Samuel Issacharoff for petitioners in No. 26-293 (*Ashton*), and no listed respondent counsel on either companion docket.

## 4. Web Searches

None attempted.
