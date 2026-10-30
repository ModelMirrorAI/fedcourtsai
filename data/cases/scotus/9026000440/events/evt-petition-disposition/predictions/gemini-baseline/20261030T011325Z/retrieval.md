# Retrieval Log

## 1. Corpus Tooling (`uv run fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 9026000440 --event evt-petition-disposition --role predictor`
   - Resolved case (`scotus/9026000440`), corpus (`corpus/corpus.db`), and event path (`data/cases/scotus/9026000440/events/evt-petition-disposition/event.yaml`).
2. `uv run fedcourts query --help`
   - Inspected available structured filter flags.
3. `uv run fedcourts query --court scotus --docket-number 20-1369 --limit 5`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 1 row: `scotus/72465404` (*Mohammed Jabateh v. United States*, No. 20-1369, originating court `ca3`, docket `18-1981`, filed `2021-03-31`, distributed `2021-09-27`, `distribution_count: 1`, `disposition: denied` on `2021-10-04`, `salience_score: 0.024`).
4. `uv run fedcourts query --court scotus --docket-number 26A102 --limit 5`
   - Transfer line: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned 1 row: `scotus/9526000102` (*Mohammed Jabateh v. United States*, No. 26A102, `application_kind: extension`, filed `2026-07-22`, `disposition: granted` on `2026-07-23`).
5. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Returned 10 recent resolved SCOTUS rows from the 2020s era for general corpus context.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Jabateh")`
   - Returned 2 published/indexed opinions:
     - `United States v. Mohammed Jabateh`, 974 F.3d 281 (3d Cir. Sept. 8, 2020) (Docket No. 18-1981, cluster_id `4783234`) — already reproduced in full in the provisioned `record/documents/appendix.txt` (App. 21a–65a).
     - `United States v. Jabateh`, Crim. No. 16-88 (E.D. Pa. Apr. 18, 2018) (cluster_id `4113585`, pre-trial/sentencing district court ruling).

## 3. Web Searches

- None attempted.
