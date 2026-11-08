# Retrieval Log — `scotus/9026000367` (`evt-petition-disposition`)

## 1. Corpus CLI Queries (`fedcourts`)

1. **Command:** `uv run fedcourts paths --court "scotus" --docket "9026000367" --event "evt-petition-disposition" --role predictor`
   - **Result:** Resolved `case_id` (`scotus/9026000367`), `corpus` (`corpus/corpus.db`), and `event` path (`data/cases/scotus/9026000367/events/evt-petition-disposition/event.yaml`).

2. **Command:** `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - **Transfer stderr:** `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - **Result:** Returned 10 recent resolved SCOTUS priors from the 2020s era (all denied interim applications from November 2026).

3. **Command:** `uv run fedcourts query --court ca5 --era 2020s --limit 10`
   - **Transfer stderr:** `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - **Result:** Returned 10 recent Fifth Circuit rows from the 2020s era.

4. **Command:** `uv run fedcourts query --court scotus --docket-number 26-367`
   - **Transfer stderr:** `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - **Result:** Returned the corpus row for `scotus/9026000367` (`Venky Venkatraman v. Bank of America, N.A.`, `docket_number: "26-367"`, `originating_court: "ca5"`, `originating_docket_number: "25-10969"`, `distribution_count: 1`, `distributed_for_conference: "2026-12-04"`, `salience_score: 0.0337`, `disposition: null`).

5. **Command:** `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - **Transfer stderr:** `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
   - **Result:** Returned 5 recent 2020s granted SCOTUS rows (`26A512`, `26-12`, `26-204`, `26A476`, `25-1103`), showing multi-distribution / high-salience profiles for granted cert petitions (`26-12` at 3 distributions, `26-204` and `25-1103` federal petitioners at 2 distributions).

6. **Command:** `uv run fedcourts query --court scotus --judge "Jones" --judge "Duncan" --judge "Douglas" --era 2020s --limit 5`
   - **Transfer stderr:** `ranged corpus reads: 699 GET(s), 183107584 byte(s)`
   - **Result:** Returned 0 rows (live-channel 2020s SCOTUS rows do not populate lower-court panel judge lists).

## 2. CourtListener MCP Calls

1. **Tool:** `mcp_courtlistener_search`
   - **Arguments:** `{"type": "o", "q": ""Midwestern Cattle" OR "Owens v. Comerica Bank"", "fields": ["caseName", "court", "dateFiled", "citation", "docketNumber"], "num_results": 10}`
   - **Result:** Returned 39 total matches (10 shown), including `Midwestern Cattle Mkt v. Legend Bank`, 999 F.3d 970 (5th Cir. 2021) (No. 20-10663) and `Owens v. Comerica Bank`, 229 S.W.3d 544 (Tex. App.—Dallas 2007) (No. 05-06-00137-CV), confirming the settled Fifth Circuit and Texas appellate caselaw relied upon by the Fifth Circuit below.

## 3. Web Searches

- None.
