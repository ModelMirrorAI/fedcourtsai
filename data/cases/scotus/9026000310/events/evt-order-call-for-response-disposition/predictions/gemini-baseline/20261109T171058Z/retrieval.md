# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. Command:
   ```bash
   uv run fedcourts query --court scotus --docket-number 26-156
   ```
   Stderr transfer line:
   `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   Result: Retrieved 1 row (`scotus/9026000156`, *Springfield R-12 School District, et al. v. Brooke Henderson, et al.*, No. 26-156, a mandatory workplace equity-training petition cited in `petition.txt` at 25 n.10, which was denied certiorari on `2026-10-05`).

2. Command:
   ```bash
   uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10
   ```
   Stderr transfer line:
   `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   Result: Retrieved 10 recent 2020s granted SCOTUS rows (`scotus/73520108`, `scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`) to inspect recent OT2026 grant patterns, distribution counts, and salience scores.

## 2. CourtListener MCP Queries

1. `mcp_courtlistener_search(type="o", case_name="De Piero v. Pennsylvania State University", filed_before="2026-10-23", fields=["caseName", "court", "dateFiled", "citation", "docketNumber"])`
   - Result: 0 results (no Third Circuit opinion filed before 2026-10-23).
2. `mcp_courtlistener_search(type="o", case_name="Diemert v. City of Seattle", filed_before="2026-10-23", fields=["caseName", "court", "dateFiled", "citation", "docketNumber"])`
   - Result: 1 result (*Diemert v. City of Seattle*, No. 25-1188, 9th Cir., filed `2026-09-28`).
3. `mcp_courtlistener_search(type="o", case_name="Chislett v. New York City", filed_before="2026-10-23", fields=["caseName", "court", "dateFiled", "citation", "docketNumber"])`
   - Result: 0 results under that exact caption string.
4. `mcp_courtlistener_search(type="o", case_name="Diemert v. City of Seattle", filed_before="2026-10-23", fields=["caseName", "court", "dateFiled", "cluster_id", "opinions", "snippet"])`
   - Result: Retrieved `cluster_id: 10985014` and `opinion_id: 11452678` for the Ninth Circuit's September 28, 2026 published opinion in *Diemert v. City of Seattle*.
5. `mcp_courtlistener_search_document(opinion_id=11452678, query="Young")`
   - Result: 0 matches in *Diemert* for `"Young"`.
6. `mcp_courtlistener_read_document(opinion_id=11452678, chunk_index=0)`
   - Result: Read summary and opening pages of *Diemert v. City of Seattle*, No. 25-1188 (9th Cir. Sept. 28, 2026) (Chief Judge Murguia).
7. `mcp_courtlistener_search_document(opinion_id=11452678, query="Chislett")`
   - Result: 20 matches in *Diemert* discussing *Chislett v. N.Y.C. Dep't of Educ.*, 157 F.4th 172 (2d Cir. 2025), and *Spengler v. Coop. Educ. Serv. Agency 7*, 180 F.4th 1015 (7th Cir. 2026).
8. `mcp_courtlistener_search_document(opinion_id=11452678, query="pervasive")`
   - Result: 7 matches in *Diemert* setting out the Ninth Circuit's "severe or pervasive" analysis.
9. `mcp_courtlistener_read_document(opinion_id=11452678, chunk_index=12)`
   - Result: Read the conclusion of *Diemert v. City of Seattle* (pages 42–44), including the discussion of *Spengler* and *Chislett*.
10. `mcp_courtlistener_read_document(opinion_id=11452678, chunk_index=[5, 6])`
    - Result: Read pages 20–26 of *Diemert v. City of Seattle*, confirming that the Ninth Circuit relied on numerous workplace incidents over a five-year span and expressly contrasted cases involving only one or two isolated incidents.
