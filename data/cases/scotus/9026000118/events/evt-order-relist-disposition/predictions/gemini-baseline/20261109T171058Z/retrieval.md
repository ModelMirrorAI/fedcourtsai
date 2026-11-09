# Precedent & Corpus Retrieval Log

## 1. Corpus Queries Executed (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-116`
   - Stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned: `scotus/9026000116` (*Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.*, No. 26-116, filed `2026-07-24`, originating court `ca11` No. `26-11828`, `distribution_count: 3`, `distributed_for_conference: "2026-11-13"`, `salience_score: 0.4169`, `disposition: null`).
2. `uv run fedcourts query --court scotus --docket-number 26-117`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/9026000117` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*, No. 26-117, filed `2026-07-24`, originating court N.D. Ala. `2:21-cv-01530-AMM`, `distribution_count: 3`, `distributed_for_conference: "2026-11-13"`, `salience_score: 0.399`, `disposition: null`).
3. `uv run fedcourts query --court scotus --docket-number 26-118`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/9026000118` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*, No. 26-118, filed `2026-07-24`, originating court N.D. Ala. `2:21-cv-1291-AMM`, `distribution_count: 3`, `distributed_for_conference: "2026-11-13"`, `salience_score: 0.399`, `disposition: null`).
4. `uv run fedcourts query --court scotus --docket-number 25-273`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: `scotus/73275215` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*, No. 25-273, filed `2025-09-10`, originating court N.D. Ala. `2:21-cv-01291-AMM`, `date_cert_granted: "2026-05-11"`, `disposition: "gvr"`, `distribution_count: 2`).
5. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1377" --citation "146 S. Ct. 1131" --citation "599 U.S. 1" --limit 10`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned: 0 rows (CLI noted that only 200 rows in `scotus` carry reporter citations in the `citations` column and directed lookups by known citation to the CourtListener MCP server).
6. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Returned: 10 recent OT2026 granted petitions/applications (`25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1166`), showing typical conference distribution counts (`2` to `5`) for granted cert dockets.
7. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (cached from prior read in same command)
   - Returned: 10 recent OT2026 GVRs (`26-5123`, `25-1269`, `25-1367`, `25-7569`, `26-139`, `26-5216`, `25-901`, `25-918`, `25-7462`, `25-7532`), notably including two Voting Rights Act Section 2 redistricting GVRs from the Ninth Circuit (`scotus/73280412`, No. 25-901, *Garcia v. Hobbs*, and `scotus/73280426`, No. 25-918, *Trevino v. Hobbs*, both GVR'd on `2026-10-05` after 2–3 distributions).
8. `uv run fedcourts query --court scotus --docket-number 25-272`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/73275212` (*Andy Luu Tran v. Herbert Jacobs*, No. 25-272, unrelated petition checked while locating the 2025 *Milligan* companion docket number).
9. `uv run fedcourts query --court scotus --docket-number 25-274`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/73275213` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*, No. 25-274, filed `2025-09-10`, originating court N.D. Ala. `2:21-cv-01530`, `date_cert_granted: "2026-05-11"`, `disposition: "gvr"`, `distribution_count: 2`).
10. `uv run fedcourts query --court scotus --disposition dismissed --era 2020s --limit 15`
    - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: 15 recent OT2026 dismissed petitions (`26-2`, `26-346`, `26-5347`, `25-1427`, `26-5287`, `26-5309`, `25-7548`, `25-7666`, `25-7693`, `26-5040`, `26-5088`, `26-5130`, `26-185`, `26-216`, `26-5089`), confirming that almost all `dismissed` cert-stage rows are 0- or 1-distribution Rule 46 or procedural dismissals.
11. `uv run fedcourts query --court scotus --docket-number 25-275`
    - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: `scotus/73275214` (*Clifford James Frost, Jr. v. Dana Nessel*, No. 25-275, unrelated petition).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Allen v. Milligan"`, `filed_after="2026-01-01"`):
   - Returned 1 result: *Allen v. Milligan*, `cluster_id: 10869022`, `opinion_id: 11336479`, `docketNumber: "25A1314"`, `dateFiled: "2026-06-02"` (608 U.S. ___, 146 S. Ct. 1377 (2026)).
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Louisiana v. Callais"`, `filed_after="2026-01-01"`):
   - Returned 2 results for *Louisiana v. Callais*, `cluster_id: 10852760`, `opinion_id: 11320154`, `docketNumber: "24-109"`, `dateFiled: "2026-04-29"` (608 U.S. ___, 146 S. Ct. 1131 (2026)) and the May 4, 2026 revision sheet.
3. `mcp_courtlistener_search` (`type="r"`, `case_name="Singleton v. Allen"`, `docket_number="2:21-cv-01291"`):
   - Returned 1 result: *Singleton v. Allen*, N.D. Ala. `2:21-cv-01291`, `docket_id: 60607496`.
4. `mcp_courtlistener_read_document` (`opinion_id=11336479`):
   - Read the full text (`52,827` chars) of the Supreme Court's June 2, 2026 per curiam stay opinion and Justice Jackson's dissent in *Allen v. Milligan*, Nos. 25A1314, 25A1315, 25A1316 (`146 S. Ct. 1377`), staying the May 26, 2026 preliminary injunctions pending appeal.
5. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=60607496`, `date_filed__gte="2026-05-01"`):
   - Returned the post-May 1, 2026 docket entries in *Singleton v. Allen* (`2:21-cv-01291`), including the May 26, 2026 Preliminary Injunction (`Doc. 363`), the June 16, 2026 joint scheduling report (`Doc. 368`), and Plaintiffs' June 22, 2026 Motion to Alter Judgment (`Doc. 369`, briefed through July 13, 2026).
6. `mcp_courtlistener_search` (`type="r"`, `case_name="Milligan v. Allen"`, `docket_number="2:21-cv-01530"`):
   - Returned 1 result: *Milligan v. Allen*, N.D. Ala. `2:21-cv-01530`, `docket_id: 61494291`.
7. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=61494291`, `date_filed__gte="2026-05-26"`):
   - Returned the post-May 26, 2026 docket entries in *Milligan v. Allen* (`2:21-cv-01530`), including the May 26, 2026 Preliminary Injunction (`Doc. 537`, quoting its operative paragraphs limited to the 2026 congressional elections), Plaintiffs' June 22, 2026 Motion to Stay Proceedings (`Doc. 544`), and Plaintiffs' June 22, 2026 Motion to Alter Judgment (`Doc. 545`).
8. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Abbott v. League of United Latin American Citizens"`, `filed_after="2025-01-01"`):
   - Returned 0 results under that full caption string.
9. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Allen v. Caster"`, `filed_after="2026-01-01"`):
   - Returned 0 results (May 11, 2026 GVR order was an order-list entry, already captured in corpus rows `25-273` and `25-274`).
10. `mcp_courtlistener_read_document` (`opinion_id=11320154`, `chunk_index=[0, 1]` and `chunk_index=2`):
    - Read the syllabus and opening sections of Justice Alito's 6–3 opinion in *Louisiana v. Callais*, 608 U.S. ___, 146 S. Ct. 1131 (Apr. 29, 2026), confirming the updated *Gingles* I–III framework and the 6–3 Justice lineup.
