# Retrieval Log

All external/corpus lookups beyond the provisioned case inputs (`data/cases/scotus/9026000293/record/` and `events/evt-order-call-for-response-disposition/event.yaml`) and stable repository references (`.github/prompts/predict.md`, `schemas/*.schema.json`, `metrics/statpack.md`) are logged below. No web searches were attempted or surfaced.

## 1. `fedcourts` CLI Lookups

1. **Path check and CLI help:**
   - Command: `uv run fedcourts paths --court "scotus" --docket "9026000293" --event "evt-order-call-for-response-disposition" --role predictor && uv run fedcourts query --help`
   - Result: Resolved `case_id` (`scotus/9026000293`), `corpus` (`corpus/corpus.db`), and `event` path, and printed `fedcourts query` flag documentation. (No ranged corpus reads.)

2. **Corpus query — 2020s SCOTUS GVR priors:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10 2>&1`
   - Stderr: `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
   - Result: Returned 10 resolved 2020s SCOTUS GVR dockets, including `25-1421` (*Casarez v. Irigoyen Farms*), `26-5528` (*Huffman v. United States*), `25-442` (*Roybal v. Griffith*, a post-CVSG GVR with `cvsg_date: "2026-06-30"` and `distribution_count: 3`), `25-1348` (*Harrington v. Martin*), `26-5123` (*Cid v. United States*), `25-1269` (*Burford German Funding v. financialright claims*), `25-1367` (*Roofing Designs by JR v. Royal American Construction*), `25-7569` (*Silva Ochoa v. United States*), `26-139` (*Monsanto Co. v. Dennis*), and `26-5216` (*Hobson v. United States*).

3. **Corpus query — 2020s SCOTUS granted cert priors:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10 2>&1`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from warm local corpus cache)
   - Result: Returned 10 resolved 2020s SCOTUS granted dockets, including `25-944` (*Robinhood Markets, Inc. v. Sodha*, post-CVSG plenary grant with `cvsg_date: "2026-06-01"` and `distribution_count: 3`), `26-239` (*Mullin v. RAICES*), `26A560` (*Mullin v. Friends of the Ruidosa Church*), `25-1408` (*Goldman Sachs Bank USA v. Brown*), `26A512` (*Scanlan v. Coalition for Open Democracy*), `26-12` (*Association for Education Fairness v. Montgomery County Board of Education*), `26-204` (*Department of Justice v. McNutt*), `26A476` (*FCC v. Brown*), `25-1103` (*U.S. DOGE Service v. U.S. District Court for D.D.C.*), and `25-7026` (*Berry v. United States*).

## 2. CourtListener MCP Lookups

1. **`mcp_courtlistener_search` — *Exxon Mobil Corp. v. Corporación CIMEX*:**
   - Parameters: `type="o"`, `court="scotus"`, `case_name="CIMEX"`, `num_results=5`, `fields=["caseName", "citation", "cluster_id", "dateFiled", "docketNumber", "opinions"]`
   - Result: Returned 1 match (`cluster_id: 10878536`, `opinion_id: 11346053`, *Exxon Mobil Corp. v. Corporación Cimex, S. A. (Cuba)*, No. 24-699, filed `2026-06-23`).

2. **`mcp_courtlistener_search` — Second Circuit *Havlish* caption lookup (first attempt):**
   - Parameters: `type="o"`, `court="ca2"`, `case_name="Havlish v. The Taliban"`, `num_results=10`, `fields=["caseName", "citation", "cluster_id", "dateFiled", "docketNumber", "opinions"]`
   - Result: `count: 0` (CourtListener indexed the case name as `"Havlish v. Taliban; Aliganga v. Taliban"` without `"The"`).

3. **`mcp_courtlistener_search` — Second Circuit `"Da Afghanistan Bank"` opinion lookup:**
   - Parameters: `type="o"`, `court="ca2"`, `q='"Da Afghanistan Bank"'`, `num_results=10`, `fields=["caseName", "citation", "cluster_id", "dateFiled", "docketNumber", "opinions"]`
   - Result: Returned 2 matches — the Second Circuit panel decision (`cluster_id: 10660852`, `opinion_id: 11127439`, *Havlish v. Taliban; Aliganga v. Taliban*, Nos. 23-258 (L), 23-354 (L), filed `2025-08-26`) and the Second Circuit order/opinions denying rehearing en banc (`cluster_id: 10811059`, `opinion_id: 11277807`, filed `2026-03-19`).

4. **`mcp_courtlistener_read_document` — *Exxon Mobil v. Corporación CIMEX* (`opinion_id=11346053`), chunks `[0, 1, 2, 3]`:**
   - Parameters: `opinion_id=11346053`, `chunk_index=[0, 1, 2, 3]`, `chunk_size=8000`
   - Result: Read Syllabus and Parts I–II.B.1 of Justice Kavanaugh's 6–3 opinion for the Court (Kagan, J., dissenting, joined by Sotomayor and Jackson, JJ.), holding that the Helms-Burton Act itself abrogates Cuban agencies' and instrumentalities' sovereign immunity.

5. **`mcp_courtlistener_read_document` — *Exxon Mobil v. Corporación CIMEX* (`opinion_id=11346053`), chunks `[5, 6]` and `[7]`:**
   - Parameters: `opinion_id=11346053`, `chunk_index=[5, 6]` (`chunk_size=8000`), followed by `chunk_index=7` (`chunk_size=8000`)
   - Result: Read Parts II.B.2–III (including the Presidential suspension gatekeeping analysis at slip op. 15–18 cited in the *Ashton* petition and Part III's rejection of implied-repeal and magic-words arguments).

6. **`mcp_courtlistener_read_document` — Second Circuit en banc denial opinions (`opinion_id=11277807`), chunks `[0, 1, 2, 3, 4, 5, 6]` and `[7, 8, 9, 10]`:**
   - Parameters: `opinion_id=11277807`, `chunk_index=[0, 1, 2, 3, 4, 5, 6]` (`chunk_size=8000`), followed by `chunk_index=[7, 8, 9, 10]` (`chunk_size=8000`)
   - Result: Read the full March 19, 2026 en banc order and opinions that had been truncated by the 150k-character cap in `petition.txt`: Judge Nardini's concurrence (joined by Judge Lohier), Judge Sullivan's dissent (joined by Chief Judge Livingston and Judges Bianco and Park), Judge Menashi's dissent (including citations to SDNY Statements of Interest by the United States), and Judges Cabranes and Calabresi's statement.

7. **`mcp_courtlistener_search_document` — Second Circuit panel opinion (`opinion_id=11127439`), query `"blocking date"`:**
   - Parameters: `opinion_id=11127439`, `query="blocking date"`, `snippet_size=500`
   - Result: Returned 3 snippets from pages 50–52 of the slip opinion confirming the panel's TRIA blocking-date holding (August 15, 2021).

8. **`mcp_courtlistener_search_document` — Second Circuit panel opinion (`opinion_id=11127439`), query `"Garnishee-Interested-Party-Appellee"`:**
   - Parameters: `opinion_id=11127439`, `query="Garnishee-Interested-Party-Appellee"`, `snippet_size=500`
   - Result: Returned 1 snippet from the caption confirming Federal Reserve Bank of New York's status as Garnishee-Interested-Party-Appellee with no separate appellate counsel appearance.
