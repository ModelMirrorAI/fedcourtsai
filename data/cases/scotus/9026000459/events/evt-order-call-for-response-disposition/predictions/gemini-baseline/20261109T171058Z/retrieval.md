# Retrieval Log

## 1. Local `fedcourts` CLI Queries

- `uv run fedcourts paths --court "scotus" --docket "9026000459" --event "evt-order-call-for-response-disposition" --role predictor`
  - Resolved `case_id: scotus/9026000459`, `corpus: corpus/corpus.db`, `event: data/cases/scotus/9026000459/events/evt-order-call-for-response-disposition/event.yaml`.
- `uv run fedcourts query --court scotus --citation "608 U.S. 391" --limit 5`
  - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
  - Returned 0 rows (with note that the corpus `citations` column holds only 200 rows of parallel cites and recommending CourtListener MCP for citation lookup).
- `uv run fedcourts query --court scotus --docket-number "26A113"`
  - `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
  - Returned `scotus/9526000113` (*Marshall Grace v. United States*, `26A113`, routine extension application granted `2026-08-14`).
- `uv run fedcourts query --court scotus --era 2020s --limit 10`
  - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
  - Returned 10 resolved 2020s SCOTUS cert priors (all `denied`).
- `uv run fedcourts query --court scotus --disposition gvr --decided-before 2026-10-29 --limit 5`
  - `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
  - Returned 5 prior SCOTUS GVR dispositions decided before `2026-10-29` (`25-1269`, `25-1367`, `25-7569`, `26-139`, `26-5216`).
- `uv run fedcourts query --court scotus --disposition granted --decided-before 2026-10-29 --limit 5`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Returned 5 prior SCOTUS granted dispositions decided before `2026-10-29` (`26A512`, `26-12`, `26-204`, `26A476`, `25-1103`).

## 2. CourtListener MCP Calls

- `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Pitchford v. Cain"`, `num_results=5`)
  - Returned 1 result: *Pitchford v. Cain*, No. 24-7351, `cluster_id=10865525`, `opinion_id=11332973`, decided `2026-05-28`.
- `mcp_courtlistener_search` (`type="o"`, `court="ca5"`, `case_name="United States v. Grace"`, `num_results=5`)
  - Returned *United States v. Grace*, No. 24-30730, `cluster_id=10829080`, `opinion_id=11294957`, decided `2026-03-27` (the decision below, already provisioned in `record/documents/decision-below.txt`), plus older unrelated Fifth Circuit cases.
- `mcp_courtlistener_read_document` (`opinion_id=11332973`, `chunk_index=0`, `chunk_size=8000`)
  - Initial call returned HTTP 429 rate-limit error (throttled for 19 seconds).
- `mcp_courtlistener_read_document` (`opinion_id=11332973`, `chunk_index=[0, 1]`, `chunk_size=8000`)
  - Two subsequent attempts returned HTTP 429 rate-limit error and one invalid-argument error (`wait_for_previous` not supported on MCP schema); fourth attempt succeeded and returned chunks 0 and 1 of *Pitchford v. Cain* (No. 24-7351, decided May 28, 2026, opinion by Kavanaugh, J., joined by Roberts, C.J., and Sotomayor, Kagan, and Jackson, JJ.; dissent by Gorsuch, J., joined by Thomas, Alito, and Barrett, JJ.).
- `mcp_courtlistener_read_document` (`opinion_id=11332973`, `chunk_index=2`, `chunk_size=8000`)
  - Succeeded and returned chunk 2 of *Pitchford v. Cain* (pages 3–6 of the slip opinion).

## 3. Web Searches

- None performed.
