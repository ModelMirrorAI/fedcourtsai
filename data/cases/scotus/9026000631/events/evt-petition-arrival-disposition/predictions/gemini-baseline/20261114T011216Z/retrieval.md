# Retrieval Log

Mode: `forward` (`DECIDED_BEFORE` unset; no web searches performed; no forecasts of this case sought or encountered).

## 1. Corpus CLI Calls (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000631" --event "evt-petition-arrival-disposition" --role predictor`
   - Returned `case_id scotus/9026000631`, `corpus corpus/corpus.db`, and event path (no corpus transfer line).
2. `uv run fedcourts query --help`
   - Inspected structured filter flags (no corpus transfer line).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 38 GET(s), 9895936 byte(s)`
   - Returned 10 recent OT2026/2020s granted SCOTUS rows (`26-239`, `26A560`, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`) showing distribution counts and counsel/salience patterns.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm local service cache)
   - Returned 10 recent OT2026/2020s denied SCOTUS rows (`26-6095`, `26A661`, `26A658`, `26A657`, `25-7515`, `25-7522`, `25-7555`, `25-1411`, `25-7656`, `25-1426`) showing `distribution_count` behavior on routine denials.
5. `uv run fedcourts query --court scotus --judge Hughes --era 2020s --limit 15`
   - Transfer: `ranged corpus reads: 744 GET(s), 194904064 byte(s)`
   - Returned 0 rows (consistent with prompt guidance that live-channel SCOTUS rows carry empty `judges`).
6. `uv run fedcourts query --court scotus --citation "596 U.S. 740" --limit 5`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows with coverage `note:` explaining sparse `citations` population on SCOTUS rows.
7. `uv run fedcourts query --court scotus --docket-number 21-234 --limit 5`
   - Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned `scotus/63246653`, *Kevin R. George v. Denis R. McDonough, Secretary of Veterans Affairs* (`21-234`), granted `2022-01-14` (`distribution_count: 2`, `salience_score: 0.098`, `originating_court: cafc`, 7 amicus counsel entries, merits affirmed `2022-06-15`), used as a benchmark for granted Federal Circuit CUE petitions under 38 U.S.C. § 5109A.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Crews v. McDonough"`, `num_results=10`)
   - Returned 3 Veterans Court / Federal Circuit entries (`Robert E. Crews v. Denis McDonough` and `Yvonne Crews v. Denis McDonough`).
2. `mcp_courtlistener_search` (`type="o"`, `q='"Haines v. West" "5109A"'`, `filed_after="2023-01-01"`, `num_results=15`)
   - Returned 2 opinions (`Crews v. McDonough`, Fed. Cir. Mar. 16, 2023, and a Veterans Court memorandum decision), confirming no circuit or en banc split post-*Crews*.
3. `mcp_courtlistener_search` (`type="o"`, `citation="63 F.4th 37"`)
   - Returned `Crews v. McDonough`, cluster `9384267`, opinion `9379743` (`63 F.4th 27`, Fed. Cir. Mar. 16, 2023; note petitioner's brief cited p. 37).
4. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q='"Crews v. McDonough" OR "Haines v. West"'`)
   - Returned 3 historical SCOTUS cert-denial order entries (`Haines v. West`, `526 U.S. 1016` (1999), and two other 1999/2000 denials), confirming no SCOTUS opinion or separate cert-denial writing citing *Crews v. McDonough*.
5. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `party_name="Crews"`)
   - Returned 0 RECAP dockets (consistent with thin SCOTUS docket coverage on CourtListener).
6. `mcp_courtlistener_read_document` (`opinion_id=9379743`, `chunk_index=[0, 1]`, `chunk_size=8000`) and follow-up single-chunk reads (`chunk_index=0` and `chunk_index=1`)
   - Read full text (15,419 chars) of *Yvonne Crews v. Denis McDonough*, 63 F.4th 27 (Fed. Cir. Mar. 16, 2023) (Hughes, J., joined by Reyna & Mayer, JJ.).
7. `mcp_courtlistener_call_endpoint` (`endpoint_id="dockets"`, `query={"court": "scotus", "case_name__icontains": "Crews", ...}`)
   - Failed with Pydantic validation error (`case_name` extra inputs not permitted for `__icontains` syntax). Did not retry endpoint after checking SCOTUS opinion search directly.
8. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q='"Yvonne Crews" OR "Crews v. McDonough"'`, `filed_after="2023-06-01"`, `filed_before="2024-07-01"`)
   - Returned 0 results (confirming no separate opinion or dissent respecting denial of certiorari in *Crews*).
9. `mcp_courtlistener_read_document` (`opinion_id=757715`, `chunk_index=[0, 1]`, `chunk_size=8000`) and follow-up single-chunk reads (`chunk_index=0` and `chunk_index=1`)
   - Read full text (15,657 chars) of *Barbara Haines v. Togo D. West, Jr.*, 154 F.3d 1298 (Fed. Cir. 1998) (Lourie, J.).
10. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Crews v. McDonough"`)
    - Returned 0 results.
11. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q="Crews"`, `filed_after="2023-09-01"`, `filed_before="2024-07-01"`)
    - Returned 4 unrelated SCOTUS merits opinions (*Starbucks Corp. v. McKinney*, *Culley v. Marshall*).
12. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q='"5109A" OR "clear and unmistakable error"'`, `filed_after="2021-01-01"`)
    - Returned 1 result: *George v. McDonough*, `596 U.S. 740` (2022) (docket `21-234`), confirming no subsequent SCOTUS opinion or separate cert-denial writing on 38 U.S.C. § 5109A.
