# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. **Attempted free-text query (syntax error):**
   - Command: `uv run fedcourts query --court scotus --q "Stinson Sentencing Guidelines commentary" --limit 10`
   - Purpose: Check corpus priors on *Stinson* and Sentencing Guidelines commentary.
   - Result: Failed (`No such option: --q`); CLI help displayed the structured flag options (`--docket-number`, `--disposition`, `--topic`, etc.).

2. **Target docket lookup:**
   - Command: `uv run fedcourts query --court scotus --docket-number "25-5343" --include-open --full`
   - Purpose: Inspect the corpus metadata for *Kendrick Jarrell Beaird v. United States* (No. 25-5343), including counsel, parties, grant date, and merits status.
   - Result: Returned row `scotus/73277583`. Confirmed `date_cert_granted: "2026-04-20"`, `distribution_count: 7`, `merits_decided: null`, `merits_judgment: null`, and listed amici (`Cato Institute`, `Court-appointed amicus curiae` represented by Anthony J. Dick, `FAMM`, `National Association of Criminal Defense Lawyers`, `National Association of Federal Defenders`, `New Civil Liberties Alliance`, `State of West Virginia`, `The Buckeye Institute`, `The Chamber of Commerce of the United States of America`).

3. **Prior *Stinson* cert petitions cited in the Brief in Opposition:**
   - Command: `uv run fedcourts query --court scotus --docket-number "23-5928" --full && uv run fedcourts query --court scotus --docket-number "23-7173" --full`
   - Purpose: Check the corpus rows for *Cortes v. United States* (No. 23-5928) and *Boler v. United States* (No. 23-7173), two prior petitions raising the *Stinson*/*Kisor* question cited at page 12 of the government's Brief in Opposition.
   - Result: Returned `scotus/72481107` (23-5928, originating from CA11) and `scotus/72482494` (23-7173, originating from CA9), both legacy stub rows without populated disposition labels in the corpus index.

## 2. External Tool Queries (CourtListener MCP)

1. **SCOTUS Docket Lookup:**
   - Tool: `mcp_courtlistener_get_endpoint_item` (`endpoint_id: "dockets"`, `item_id: 73277583`)
   - Purpose: Check docket metadata for *Beaird v. United States* (No. 25-5343).
   - Result: Confirmed `id: 73277583`, `case_name: "Kendrick Jarrell Beaird v. United States"`, `docket_number: "25-5343"`, `date_filed: "2025-08-13"`, `date_argued: "2026-10-13"`, `date_terminated: null`.

2. **Precedent Opinion Search (*Kisor v. Wilkie*):**
   - Tool: `mcp_courtlistener_search` (`type: "o"`, `court: "scotus"`, `case_name: "Kisor v. Wilkie"`)
   - Purpose: Verify citation and cluster metadata for *Kisor v. Wilkie*.
   - Result: Confirmed *Kisor v. Wilkie*, 588 U.S. 558, 139 S. Ct. 2400 (decided June 26, 2019).

3. **Docket Entries Endpoint Call:**
   - Tool: `mcp_courtlistener_call_endpoint` (`endpoint_id: "docket-entries"`, `query: {"docket": 73277583}`)
   - Purpose: Check whether CourtListener held PACER/RECAP docket entries for SCOTUS docket 73277583.
   - Result: Returned 0 results (SCOTUS dockets on CourtListener do not populate PACER `docket-entries` unless linked to an opinion or oral argument).

4. **Additional Opinion / Oral Argument Searches (Throttled by Rate Limit):**
   - Tool: `mcp_courtlistener_search` for *Beaird v. United States*, *Loper Bright Enterprises v. Raimondo*, and *Stinson v. United States*.
   - Result: Returned HTTP 429 rate-limit error (25 requests/min shared bucket). Did not retry because the provisioned record (`petition.txt`, `brief-in-opposition.txt`, `appendix.txt`, `2026-04-21.json`) already contained the complete procedural history, the grant order text limiting review to Question 2, the circuit split details, and the Solicitor General's concession that *Kisor* governs *Stinson*.
