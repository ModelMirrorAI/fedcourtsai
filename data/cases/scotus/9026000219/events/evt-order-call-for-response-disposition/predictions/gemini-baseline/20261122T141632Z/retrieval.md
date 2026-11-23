# Retrieval Log

Mode: `forward` (`record/context.json` `cutoff = "2026-09-15"`, `moment = "response-requested"`). Per the prompt rules, no queries were made for this docket's own post-snapshot history, filings, or disposition.

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000219" --event "evt-order-call-for-response-disposition" --role predictor && echo "DECIDED_BEFORE=${DECIDED_BEFORE:-unset}" && uv run fedcourts query --help`
   - Resolved cell paths (`case_id = scotus/9026000219`, `DECIDED_BEFORE=unset`) and inspected `fedcourts query` flags (also re-displayed `uv run fedcourts query --help | cat` without truncation).
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15`
   - Stderr: `ranged corpus reads: 44 GET(s), 11403264 byte(s)`
   - Returned 15 resolved 2020s SCOTUS granted rows (cert petitions and applications) for distribution, salience, and originating-court comparison.
3. `uv run fedcourts query --court scotus --citation "468 U.S. 897" --citation "565 U.S. 535" --limit 10`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows plus CLI note explaining that `citations` indexes a case's own parallel citations rather than citing-case edges.
4. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 resolved 2020s SCOTUS denied rows for comparison of distribution counts and salience bands on denied dockets.

## 2. Committed Statpack Reads (beyond provisioned `record/`)

- Read `metrics/statpack.md` in full and inspected the `United States Court of Appeals for the Armed Forces` bucket in `metrics/statpack.json` (`103` cases, `98` resolved, `5` open: `96` denied [`98.0%`], `2` granted [`2.04%`]).

## 3. CourtListener MCP Lookups (Historical Precedent and CAAF Cert Priors)

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Lattin" OR "Mil. R. Evid. 315" OR "Mil. R. Evid. 311" OR "military commander" "search authorization""`, `num_results=10`)
   - `query_id="d34b26ba"`, `count=1` (*Florida v. Jimeno*, 500 U.S. 248 (1991)).
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Shadwick v. City of Tampa"`, `num_results=5`)
   - `query_id="f847c9cb"`, `count=2` (*Shadwick v. City of Tampa*, 407 U.S. 345 (1972), `cluster_id=108582`).
3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Court of Appeals for the Armed Forces" certiorari granted OR denied"`, `num_results=10`)
   - `query_id="3cf0f614"`, `count=91` (historical SCOTUS certiorari order entries from CAAF).
4. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Court of Appeals for the Armed Forces""`, `filed_after="2018-01-01"`, `filed_before="2026-09-01"`, `order_by="dateFiled desc"`, `num_results=20`, including `opinions`)
   - `query_id="71e14423"`, `count=29` (recent SCOTUS opinions and orders referencing CAAF).
5. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=108582`, `fields=["id", "case_name", "date_filed", "syllabus", "sub_opinions"]`)
   - Retrieved cluster metadata for *Shadwick v. City of Tampa*, 407 U.S. 345 (1972) (`opinion_id=108582`).
6. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Lattin v. United States"`, `num_results=5`)
   - `query_id="623e6502"`, `count=0`.
7. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Perkins v. United States"`, `filed_after="2019-01-01"`, `filed_before="2021-01-01"`, `num_results=10`)
   - `query_id="643c464b"`, `count=1` (*Perkins v. United States*, 140 S. Ct. 982 (2020), arising from CA8 rather than CAAF).
8. `mcp_courtlistener_read_document` (`opinion_id=108582`, `chunk_index=0`)
   - Read opening chunk of *Shadwick v. City of Tampa*, 407 U.S. 345 (1972), holding that non-lawyer municipal court clerks may issue Fourth Amendment warrants if neutral, detached, and capable of determining probable cause.
9. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `case_name="Lattin v. United States"`, `num_results=5`)
   - `query_id="fb2998d6"`, `count=0`.
10. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Messerschmidt v. Millender"`, `num_results=5`)
    - `query_id="d0402ece"`, `count=6` (*Messerschmidt v. Millender*, 565 U.S. 535 (2012), `opinion_id=623242`).
11. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Court of Appeals for the Armed Forces" granted OR denied"`, `filed_after="2021-01-01"`, `filed_before="2026-08-01"`, `order_by="dateFiled desc"`, `num_results=20`)
    - `query_id="8b637647"`, `count=5`.
12. `mcp_courtlistener_search_document` (`opinion_id=623242`, `query="deputy district attorney"`)
    - Returned 9 snippets in *Messerschmidt v. Millender* holding that pre-submission review and approval by a deputy district attorney supports objective reasonableness under *Leon*/*Malley*.
13. `mcp_courtlistener_search_document` (`opinion_id=623242`, `query="Leon"`)
    - Returned 20 of 40 snippets in *Messerschmidt v. Millender* on the high threshold for overcoming *Leon* good faith.
14. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Court of Appeals for the Armed Forces""`, `filed_after="2018-01-01"`, `filed_before="2026-08-15"`, `order_by="dateFiled desc"`, `num_results=25`, compact fields)
    - `query_id="ff93bc48"`, `count=29` (confirming that the modern CAAF certiorari grants — *United States v. Briggs*, No. 19-108, and *United States v. Collins*, No. 19-184, 592 U.S. 69 (2020) — were Solicitor General petitions).

## 4. Web Searches

- None attempted.
