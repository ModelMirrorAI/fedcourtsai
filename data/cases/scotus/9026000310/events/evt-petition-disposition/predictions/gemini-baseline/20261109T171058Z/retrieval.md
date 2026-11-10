# Retrieval Log

## 1. Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000310" --event "evt-petition-disposition" --role predictor`
   - Result: Resolved `case_id` (`scotus/9026000310`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts query --help`
   - Result: Printed CLI flags and usage documentation.
3. `uv run fedcourts query --court scotus --docket-number 26-156`
   - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned 1 row (`scotus/9026000156`, *Springfield R-12 School District, et al. v. Brooke Henderson, et al.*, docket `26-156`, originating from CA8 `23-1374, 23-1880`, distributed once for `2026-09-28`, `disposition: "denied"`, `date_cert_denied: "2026-10-05"`).
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Result: Returned 10 recent OT2026 granted SCOTUS rows (including `25-1408`, `26-12` *Association for Education Fairness v. Montgomery County Board of Education*, `26-204`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, and stay applications `26A512`, `26A476`).
5. `uv run fedcourts query --court ca10 --judge "Bacharach" --limit 5`
   - Transfer line: `ranged corpus reads: 42 GET(s), 11010048 byte(s)`
   - Result: Returned 0 rows (judge lists on circuit slice rows are withheld in the corpus).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", case_name="De Piero v. Pennsylvania State University", fields=["caseName", "court", "dateFiled", "docketNumber", "citation"])`
   - Result: 0 matches in the opinion index under the full party name.
2. `mcp_courtlistener_search(type="o", case_name="Diemert v. City of Seattle", fields=["caseName", "court", "dateFiled", "docketNumber", "citation"])`
   - Result: 1 match — *Diemert v. City of Seattle*, No. 25-1188 (9th Cir. filed Sept. 28, 2026).
3. `mcp_courtlistener_search(type="o", case_name="Diemert v. City of Seattle", fields=["caseName", "court", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Result: Returned `cluster_id: 10985014`, `opinion_id: 11452678`.
4. `mcp_courtlistener_search(type="o", case_name="De Piero", fields=["caseName", "court", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Result: 2 unrelated matches (Puerto Rico Court of Appeals and a 2001 Ninth Circuit opinion).
5. `mcp_courtlistener_read_document(opinion_id=11452678, chunk_index=[0, 1])`
   - Result: Read chunks 0 and 1 of *Diemert v. City of Seattle*, No. 25-1188 (9th Cir. Sept. 28, 2026) (Chief Judge Murguia, joined by Judges W. Fletcher and Koh).
6. `mcp_courtlistener_read_document(opinion_id=11452678, chunk_index=[3, 4])`
   - Result: Read chunks 3 and 4 of *Diemert v. City of Seattle*, covering the Title VII hostile-work-environment legal standard and citations to *Chislett*, *Ames*, and *De Piero*.
7. `mcp_courtlistener_read_document(opinion_id=11452678, chunk_index=[5])`
   - Result: Read chunk 5 of *Diemert v. City of Seattle*, detailing the ten multi-year workplace harassment incidents that distinguished *Diemert* from isolated-incident cases.
