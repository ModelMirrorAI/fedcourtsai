# Retrieval Log — `scotus/9026000369` (`evt-petition-disposition`)

## 1. Corpus CLI (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000369" --event "evt-petition-disposition" --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query --help`
   - Inspected CLI options and filter rules.
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Retrieved 10 recent 2020s SCOTUS denied priors.
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Retrieved 10 recent 2020s SCOTUS granted priors (including OT2026 grants with distribution counts and salience scores).
5. `uv run fedcourts query --court scotus --citation "544 U.S. 280" --limit 5`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows (sparse citation column note).
6. `uv run fedcourts query --court scotus --docket-number "26-369" --limit 5`
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Returned the corpus metadata row for `scotus/9026000369` (`26-369`).
7. `uv run fedcourts query --court ca9 --judge "Barry G. Silverman" --judge "Jacqueline H. Nguyen" --judge "Andrew D. Hurwitz" --limit 5`
   - `ranged corpus reads: 134 GET(s), 35127296 byte(s)`
   - Returned 0 rows (circuit judge lists withheld in corpus slice).
8. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
   - Retrieved 10 recent 2020s SCOTUS GVR priors.

## 2. CourtListener MCP Server

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="University of Maryland Medical System", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Returned 0 results (due to `"Md."` abbreviation in case name).
2. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2025-10-01", q=""Rooker-Feldman"", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Returned 2 results for *T. M. v. University of Md. Medical System Corporation*, No. 25-197 (decided June 18, 2026), cluster IDs `10877643` and `10876934`, opinion ID `11345156`.
3. `mcp_courtlistener_search(type="o", court="ca9", case_name="Loop v. State of Washington", fields=["caseName", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Returned 0 results (the Ninth Circuit memorandum disposition of March 20, 2026 is already reproduced in full in the provisioned `record/documents/appendix.txt` at App-1 to App-2).
4. `mcp_courtlistener_read_document(opinion_id=11345156, chunk_index=0, chunk_size=8000)`
   - Read the first part of the syllabus in *T. M. v. University of Md. Medical System Corp.*, No. 25-197 (June 18, 2026).
5. `mcp_courtlistener_read_document(opinion_id=11345156, chunk_index=1, chunk_size=8000)`
   - Read the remainder of the syllabus and vote lineup in *T. M. v. University of Md. Medical System Corp.*, No. 25-197 (June 18, 2026).

## 3. Web Searches

- None performed.
