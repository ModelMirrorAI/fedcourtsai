# Retrieval Log

Mode: `forward` (`DECIDED_BEFORE` unset; `cutoff: 2026-11-17`). No third-party forecasts or commentary were sought or encountered.

## 1. Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000293" --event "evt-order-cvsg-disposition" --role predictor` and `uv run fedcourts query --help`
   - Confirmed case/event paths and CLI filter flags; no ranged corpus reads.
2. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1909" --limit 5`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (CLI noted that only 195 SCOTUS rows populate reporter citations and directed single-case citation lookup to the CourtListener MCP server).
3. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Stderr: `ranged corpus reads: 38 GET(s), 9895936 byte(s)`
   - Returned 10 recent 2020s SCOTUS GVR priors (including post-CVSG GVR `25-442`, *Roybal v. Griffith*, showing `distribution_count: 3` after CVSG).
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from cached blocks in the same shell invocation / local cache)
   - Returned 10 recent 2020s SCOTUS granted priors (including post-CVSG plenary grant `25-944`, *Robinhood Markets v. Sodha*, showing `distribution_count: 3` after CVSG).
5. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent 2020s SCOTUS denied priors for distribution-count and salience comparison.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="146 S. Ct. 1909", num_results=5, fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])`
   - Returned 2 unrelated older opinions matching partial token overlap; `146 S. Ct. 1909` was not yet indexed under that reporter string on CourtListener.
2. `mcp_courtlistener_search(type="o", citation="170 F.4th 100", num_results=5, fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])`
   - Returned 0 results (reporter cite not yet attached to the cluster).
3. `mcp_courtlistener_search(type="o", case_name="Havlish v. Taliban", court="ca2", num_results=10, fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])`
   - Returned 2 clusters: `cluster_id: 10660852` / `opinion_id: 11127439` (August 26, 2025 panel decision) and `cluster_id: 10855838` / `opinion_id: 11277807` (March 19, 2026 order and opinions denying rehearing en banc).
4. `mcp_courtlistener_search(type="o", case_name="Exxon Mobil CIMEX", court="scotus", num_results=5, fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions"])`
   - Returned 1 cluster: *Exxon Mobil Corp. v. Corporación Cimex, S. A. (Cuba)* (`cluster_id: 10878560` / `opinion_id: 11346053`, decided June 23, 2026).
5. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0, 1, 2, 3], chunk_size=8000)`
   - Read chunks 0–3 of the Second Circuit March 19, 2026 en banc rehearing denial opinions (omitted by the appendix cap in `petition.txt`).
6. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[4, 5, 6, 7], chunk_size=8000)`
   - Read chunks 4–7 of the Second Circuit March 19, 2026 en banc rehearing opinions (Judge Sullivan's and Judge Menashi's dissents).
7. `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[8, 9, 10], chunk_size=8000)`
   - Read chunks 8–10 (conclusion of Judge Menashi's dissent and the panel majority's statement respecting denial of rehearing en banc).
8. `mcp_courtlistener_read_document(opinion_id=11127439, chunk_index=[7, 8, 9, 10], chunk_size=8000)`
   - Read Part II.C.1 of the August 26, 2025 Second Circuit panel opinion confirming the panel's express holding that TRIA § 201(a) abrogates both FSIA jurisdictional immunity and FSIA execution immunity.
9. `mcp_courtlistener_read_document(opinion_id=11346053, chunk_index=[0, 1, 2, 3, 4], chunk_size=8000)` and `mcp_courtlistener_read_document(opinion_id=11346053, chunk_index=[5, 6, 7, 8], chunk_size=8000)`
   - Read the syllabus and majority opinion of *Exxon Mobil Corp. v. Corporación Cimex, S. A. (Cuba)* (June 23, 2026) to evaluate petitioners' *Cimex* GVR argument.

## 3. Web Lookups (`web_fetch`)

1. `web_fetch` requesting Questions Presented from `https://www.supremecourt.gov/qp/26-00292qp.pdf` and `https://www.supremecourt.gov/qp/26-00294qp.pdf` and PDF links from `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-292.html` and `26-293.html`.
   - Outcome: Supreme Court `qp/` PDFs are published only after certiorari is granted (so those URLs do not exist for pending CVSG petitions), and `search.aspx` populates docket tables via client-side JavaScript. As a result, `web_fetch`'s sub-summarizer returned fabricated placeholder URLs and text (immediately identified by cross-checking against the provisioned `2026-11-16.json` and `26-292.json` snapshots, e.g., fake `1234567` timestamps and wrong filing dates). That `web_fetch` response was disregarded in full, and no forecast or commentary appeared.
