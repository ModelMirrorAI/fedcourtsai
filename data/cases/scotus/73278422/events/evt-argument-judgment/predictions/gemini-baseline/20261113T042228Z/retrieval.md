# Retrieval Log (`scotus/73278422` — `evt-argument-judgment`)

All lookups attempted beyond the provisioned inputs in `data/cases/scotus/73278422/`, including failed CLI flag invocations:

## 1. Local Corpus CLI (`fedcourts query`)

1. **Attempted (failed — exit code 2, `No such option: --stage`):**
   - Command: `uv run fedcourts query --stage merits --originating-circuit ca9 --log-for scotus/73278422 --limit 20 && uv run fedcourts query --stage merits --topic "Bivens" --log-for scotus/73278422 --limit 20 && uv run fedcourts query --case-name "Cisco" --log-for scotus/73278422 --limit 10`
   - Result: Usage error explaining structured filter flags (`--court`, `--disposition`, `--era`, `--docket-number`, etc.).

2. **Attempted (failed — exit code 2, `No such option: --log-for`):**
   - Command: `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15 --log-for scotus/73278422 && uv run fedcourts query --court scotus --docket-number 24-856 --full --log-for scotus/73278422 && uv run fedcourts query --court scotus --docket-number 24-809 --full --log-for scotus/73278422`
   - Result: Usage error rejecting `--log-for`.

3. **Succeeded — SCOTUS 2020s granted priors and dockets `24-856` (*Cisco Systems*) & `24-809` (*Goldey v. Fields*):**
   - Command: `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10 && uv run fedcourts query --court scotus --docket-number 24-856 && uv run fedcourts query --court scotus --docket-number 24-809`
   - Transfer lines reported:
     - `ranged corpus reads: 42 GET(s), 10944512 byte(s)` (returned 10 recent 2020s granted SCOTUS rows)
     - `ranged corpus reads: 18 GET(s), 4718592 byte(s)` (returned `scotus/72487129`, *Cisco Systems, Inc., et al. v. Doe I, et al.*, No. 24-856, `merits_judgment: "reversed"`, `merits_decided: "2026-06-23"`)
     - `ranged corpus reads: 1 GET(s), 262144 byte(s)` (returned `scotus/70670998`, *Howard Goldey, Associate Warden, et al. v. Andrew Fields, III, et al.*, No. 24-809, `merits_judgment: "reversed"`, `merits_decided: "2025-06-30"`)

## 2. CourtListener MCP Lookups (Precedent & Sitting Calendar Only; Zero Queries on This Case)

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Cisco Systems"`, `num_results=5`): Returned *Cisco Systems, Inc. v. Doe*, cluster `10878537`, opinion `11346054`, filed `2026-06-23` (Barrett, J.).
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Goldey v. Fields"`, `num_results=5`): Returned *Goldey v. Fields*, 606 U.S. 942, cluster `10776815`, opinion `11243402`, filed `2025-06-30` (Per Curiam).
3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Egbert v. Boule"`, `num_results=5`): Returned *Egbert v. Boule*, 596 U.S. 482, cluster `6337760`, opinion `6347905`, filed `2022-06-08` (Thomas, J.).
4. `mcp_courtlistener_read_document` (`opinion_id=11243402`, full text): Read full slip opinion of *Goldey v. Fields*, 606 U.S. 942 (2025) (confirming per curiam reversal with no noted dissents and the PLRA / prison-administration / BOP ARP special-factors holding).
5. `mcp_courtlistener_read_document` (`opinion_id=11346054`, `chunk_index=[0, 1, 2]`, `chunk_size=8000`): Read syllabus and lineup of *Cisco Systems, Inc. v. Doe* (June 23, 2026).
6. `mcp_courtlistener_search_document` (`opinion_id=11346054`, `query="Bivens"`, `snippet_size=500`): Located 2 matches comparing ATS implied causes of action to *Bivens* and *Egbert*.
7. `mcp_courtlistener_read_document` (`opinion_id=11346054`, `chunk_index=[3, 4, 5, 6]`, `chunk_size=8000`) and (`chunk_index=7`, `chunk_size=8000`): Read Justice Barrett's majority opinion in *Cisco Systems*, including Footnote 3 ("this far and no further" on preserving the historical "Blackstone three" ATS actions without revisiting reliance interests).
8. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="FS Credit Opportunities"`, `num_results=3`): Returned *FS Credit Opportunities Corp. v. Saba Capital Master Fund, Ltd.*, cluster `10873664`, opinion `11341135`, filed `2026-06-11`.
9. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Trump v. Slaughter"`, `num_results=3`): Returned *Trump v. Slaughter*, cluster `10881681`, filed `2026-06-29`.
10. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="National Republican Senatorial Committee"`, `num_results=3`): Returned *NRSC v. FEC*, cluster `10882240`, filed `2026-06-29`.
11. `mcp_courtlistener_read_document` (`opinion_id=11341135`, `chunk_index=[0, 1]`, `chunk_size=4000`) and (`chunk_index=2`, `chunk_size=4000`): Read syllabus and 6–3 lineup of *FS Credit Opportunities Corp. v. Saba Capital* (Barrett, J., joined by Roberts, Thomas, Alito, Gorsuch, Kavanaugh; Sotomayor, Kagan, Jackson dissenting).
12. `mcp_courtlistener_search` (`type="oa"`, `court="scotus"`, `argued_after="2026-11-01"`, `argued_before="2026-11-10"`, `num_results=20`): Retrieved the 7 argued cases in the November 2026 Supreme Court argument sitting to gauge sitting opinion-assignment load.
13. `mcp_courtlistener_read_document` (`opinion_id=6347905`, `chunk_index=0`, `chunk_size=4000`), (`chunk_index=2`, `chunk_size=4000`), (`chunk_index=3`, `chunk_size=2000`), and (`chunk_index=6`, `chunk_size=2000`): Read syllabus and exact vote/writing lineup in *Egbert v. Boule*, 596 U.S. 482 (2022).

## 3. Web Searches

None attempted.
