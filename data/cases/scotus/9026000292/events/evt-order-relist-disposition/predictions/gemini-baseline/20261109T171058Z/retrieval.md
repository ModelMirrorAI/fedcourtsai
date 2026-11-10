# Retrieval Log

## 1. Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-292`
   - Transfer stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned 1 row (`scotus/9026000292`, *Fiona Havlish, et al. v. The Taliban, et al.*, `distribution_count: 2`, `salience_score: 0.1008`, `originating_court: ca2`).

2. `uv run fedcourts query --court scotus --docket-number 26-293`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 1 row (`scotus/9026000293`, *Kathleen Ashton, et al. v. The Taliban, et al.*, `distribution_count: 2`, `salience_score: 0.1008`, `originating_court: ca2`).

3. `uv run fedcourts query --court scotus --docket-number 26-294`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 1 row (`scotus/9026000294`, *James Owens, et al. v. The Taliban, et al.*, `distribution_count: 2`, `salience_score: 0.1008`, `originating_court: ca2`).

4. `uv run fedcourts query --court ca2 --judge Cabranes --judge Calabresi --judge Sullivan --limit 5`
   - Transfer stderr: `ranged corpus reads: 80 GET(s), 20971520 byte(s)`
   - Result: 0 rows returned (judge filter is sparsely populated on CA2 rows).

5. `uv run fedcourts query --court scotus --originating-court ca2 --distribution-count 2 --limit 15`
   - Transfer stderr: None (CLI usage error: `No such option: --originating-court`).

6. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer stderr: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
   - Result: Returned 10 recent OT2026 granted rows (`25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", citation="152 F.4th 339", fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "opinions"])`
   - Result: 0 results (reporter citation not yet indexed on the cluster).

2. `mcp_courtlistener_search(type="o", citation="170 F.4th 100", fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "opinions"])`
   - Result: 0 results (reporter citation not yet indexed on the cluster).

3. `mcp_courtlistener_search(type="o", court="ca2", case_name="Havlish v. The Taliban", fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "opinions"])`
   - Result: 0 results (indexed under *Havlish v. Taliban; Aliganga v. Taliban*).

4. `mcp_courtlistener_search(type="o", court="ca2", docket_number="23-258", fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "opinions"])`
   - Result: 2 results returned for Second Circuit Docket No. 23-258 (*Havlish v. Taliban; Aliganga v. Taliban*):
     - `cluster_id: 10660852`, `opinion_id: 11127439` (panel opinion and dissent, filed 2025-08-26)
     - `cluster_id: 10811157`, `opinion_id: 11277807` (en banc denial order, concurrence, and dissents, filed 2026-03-19)

5. `mcp_courtlistener_search(type="o", court="ca2", q=""Da Afghanistan Bank" "Taliban"", fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "opinions"])`
   - Result: Returned the same 2 Second Circuit clusters (`10660852` and `10811157`).

6. `mcp_courtlistener_read_document(opinion_id=11277807)`
   - Result: Retrieved full text (82,791 chars) of the March 19, 2026 Second Circuit order denying rehearing en banc, the concurrence by Judges Cabranes and Calabresi, Judge Sullivan's dissent (joined by Judges Nardini, Park, and Menashi), and Judge Menashi's dissent (joined by Judges Sullivan, Nardini, and Park).

7. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[4, 5, 6, 7, 8, 9], chunk_size=8000)`
   - Result: Retrieved chunks 4–9 of the August 26, 2025 Second Circuit panel opinion (156,644 chars total across 20 chunks), covering the FSIA analysis and the start of the TRIA analysis.

8. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19], chunk_size=8000)`
   - Result: Retrieved chunks 10–19 of the August 26, 2025 Second Circuit panel opinion, covering the remainder of the majority's TRIA "time of blocking" analysis and the full text of Judge Sullivan's panel opinion concurring in part and dissenting in part.

## 3. Web Searches

None.
