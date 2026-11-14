# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "547 U.S. 319" --citation "410 U.S. 284" --limit 20`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned: 0 rows, with a coverage note explaining that `--citation` matches a case's own parallel reporter citations rather than a citing-cases graph.

2. `uv run fedcourts query --court scotus --era 2020s --limit 15`
   - Transfer: `ranged corpus reads: 9 GET(s), 2293760 byte(s)`
   - Returned: 15 recent 2020s resolved SCOTUS rows (used to inspect recent cert and interim dispositions, salience bands, and distribution counts).

3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 20`
   - Transfer: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
   - Returned: 20 recent granted 2020s SCOTUS rows (checked for any pending OT2026 merits overlap on Sixth Amendment complete-defense or Rule 403 issues).

4. `uv run fedcourts query --court scotus --disposition granted --limit 50`
   - Transfer: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
   - Returned: 50 recent granted SCOTUS rows across OT2025–OT2026 (confirmed no pending granted merits case overlaps the evidentiary or military-justice question presented here).

## CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Court of Appeals for the Armed Forces" "1259""`, `num_results=10`)
   - Returned: 5 SCOTUS opinions referencing CAAF and 28 U.S.C. § 1259 (*Cox v. United States*, *Ortiz v. United States*, *United States v. Denedo*, *Clinton v. Goldsmith*, *Davis v. United States*).

2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Court of Appeals for the Armed Forces""`, `filed_after="2018-01-01"`, `fields=["caseName","dateFiled","docketNumber","citation","status"]`, `num_results=15`)
   - Returned: 15 of 29 matches (primarily *Ortiz* trailer orders and *United States v. Briggs*, 592 U.S. 69 (2020)).

3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Holmes v. South Carolina" "right to present a complete defense""`, `filed_after="2010-01-01"`, `fields=["caseName","dateFiled","docketNumber","citation","status"]`, `num_results=15`)
   - Returned: 2 matches, both for *Nevada v. Jackson*, 569 U.S. 505 (2013) (per curiam).

4. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `citation="569 U.S. 505"`, `fields=["caseName","cluster_id","opinions","syllabus"]`, `num_results=3`)
   - Returned: Cluster metadata and opinion ID `873668` for *Nevada v. Jackson*, 569 U.S. 505 (2013).

5. `mcp_courtlistener_search` (`type="o"`, `court="armfor"`, `q=""Maebane" OR ("Holmes v. South Carolina" "403")"`, `fields=["caseName","dateFiled","citation","cluster_id","opinions"]`, `num_results=5`)
   - Returned: 5 of 7 CAAF opinions, led by *United States v. Maebane*, 86 M.J. 173 (C.A.A.F. 2025) (`opinion_id=11143659`).

6. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Court of Appeals for the Armed Forces""`, `filed_after="2023-01-01"`, `fields=["caseName","dateFiled","docketNumber","citation"]`, `num_results=15`)
   - Returned: 3 SCOTUS opinions mentioning CAAF since 2023 (*Kennedy v. Braidwood Management, Inc.* and *Trump v. Cook*), confirming no recent SCOTUS merits decisions on CAAF evidentiary appeals.

7. `mcp_courtlistener_read_document` (`opinion_id=873668`, `chunk_index=0`, `chunk_size=8000`)
   - Returned: Chunk 0 of 3 (21,910 total chars) of *Nevada v. Jackson*, 569 U.S. 505 (2013).

8. `mcp_courtlistener_search_document` (`opinion_id=11143659`, `query="complete defense"`, `snippet_size=500`)
   - Returned: 5 snippets from *United States v. Maebane*, 86 M.J. 173 (C.A.A.F. 2025), confirming CAAF applies the standard *Holmes*/*Chambers* Sixth Amendment framework.

9. `mcp_courtlistener_read_document` (`opinion_id=873668`, `chunk_index=1`, `chunk_size=8000`)
   - Returned: Chunk 1 of 3 of *Nevada v. Jackson*, 569 U.S. 505 (2013).

10. `mcp_courtlistener_read_document` (`opinion_id=873668`, `chunk_index=2`, `chunk_size=8000`)
    - Returned: Chunk 2 of 3 of *Nevada v. Jackson*, 569 U.S. 505 (2013).

11. `mcp_courtlistener_search` (`type="o"`, `court="ca11"`, `docket_number="25-12042"`, `fields=["caseName","dateFiled","docketNumber","syllabus","posture"]`, `num_results=3`)
    - Returned: 0 published opinion results for 11th Cir. No. 25-12042 (*Berry v. United States*).

## Web Searches

None attempted.
