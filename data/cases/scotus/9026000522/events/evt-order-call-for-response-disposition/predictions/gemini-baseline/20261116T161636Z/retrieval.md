# Retrieval Log

Mode: `forward` (`record/context.json`). All lookups attempted beyond the provisioned files in `data/cases/scotus/9026000522/record/` and committed repository docs/statpack:

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --stage cert --moment response-requested --limit 20`
   - Result: CLI usage error (`No such option: --stage`); no ranged corpus reads executed.
2. `uv run fedcourts query --court scotus --docket-number 25-819`
   - Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned 1 row — `scotus/73279958`, *Jeanne Hedgepeth v. James A. Britton, et al.*, No. 25-819 (`originating_court: ca7`, `distribution_count: 2`, `disposition: denied` on `2026-05-18`, `has_opinion: false`, 7 amicus counsel entries).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 30 GET(s), 7798784 byte(s)`
   - Result: Returned 5 recent 2020s SCOTUS granted rows (`25-944`, `26-239`, `26A560`, `25-1408`, `26A512`) for salience/distribution context.
4. `uv run fedcourts query --court scotus --citation "606 U.S. 937"`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: 0 rows (`note: citations filter: only 195 row(s) in scope (scotus) carry any reporter citation at all...`).

## Official Supreme Court Docket (`web_fetch`)

5. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-522.html`
   - Result: Retrieved official docket entries for No. 26-522 through November 13, 2026. Confirmed case remains pending after the November 2, 2026 Call for Response (due December 2, 2026), with two post-snapshot entries: `Nov 06 2026: Brief amicus curiae of Illinois Council of Police filed` and `Nov 13 2026: Motion of Annette Nance-Holt, et al. for an extension of time submitted`.

## CourtListener MCP Lookups

6. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="MacRae v. Mattos"`)
   - Result: 0 results under default status filter.
7. `mcp_courtlistener_search` (`type="o"`, `court="ca1"`, `case_name="Hussey v. City of Cambridge"`)
   - Result: 1 result — First Circuit panel opinion `cluster_id: 10654927` (`dateFiled: 2025-08-15`, `opinion_id: 11121514`); confirmed no en banc merits opinion has issued yet.
8. `mcp_courtlistener_search` (`type="r"`, `court="ilnd"`, `docket_number="1:22-cv-04982"`)
   - Result: 1 result — *Inendino v. Nance-Holt*, N.D. Ill. `docket_id: 65347166` (`dateFiled: 2022-09-14`).
9. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""MacRae" "Mattos" "Pickering""`)
   - Result: 0 results under default status filter.
10. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=65347166`, `entry_number__in="1,43,96,124,125,126,127"`)
    - Result: Endpoint parameter validation error on `entry_number__in`.
11. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""MacRae" "Pickering""`, `stat_Published=true, stat_Relating-to=true, stat_Separate=true, stat_Unpublished=true`)
    - Result: 1 result — *MacRae v. Mattos*, `cluster_id: 10619929` (`dateFiled: 2025-06-30`, `opinion_id: 11086517`, Statement of Thomas, J., respecting denial of certiorari).
12. `mcp_courtlistener_search` (`type="rd"`, `court="ilnd"`, `docket_number="1:22-cv-04982"`, `q="complaint OR "qualified immunity" OR reinstatement OR Monell"`, `num_results=30`)
    - Result: Returned 30 of 32 matching RECAP document entries on N.D. Ill. docket `65347166`, including Dkt. 32 Memorandum Opinion and Order (`recap_document_id: 231330967`), Dkt. 43 First Amended Complaint entry text, and Dkt. 96/136 summary-judgment entries.
13. `mcp_courtlistener_search` (`type="d"`, `court="ca1"`, `docket_number="24-1279"`)
    - Result: 1 result — *Hussey v. City of Cambridge*, `docket_id: 68475025` (`dateFiled: 2024-03-26`).
14. `mcp_courtlistener_read_document` (`opinion_id=11086517`)
    - Result: Read full text (`17701` chars) of Justice Thomas's solo statement respecting the denial of certiorari in *MacRae v. Mattos*, No. 24-355, 606 U.S. 937 (June 30, 2025).
15. `mcp_courtlistener_read_document` (`recap_document_id=231330967`)
    - Result: Read full text (`27430` chars) of Judge Durkin's March 3, 2023 Memorandum Opinion and Order on motions to dismiss in *Inendino v. Lightfoot*, No. 22 C 04982 (N.D. Ill.).
16. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Hedgepeth" "Britton""`, `stat_Published=true, stat_Relating-to=true, stat_Separate=true, stat_Unpublished=true`)
    - Result: 1 unrelated opinion citing an older *Hedgepeth* decision (*Nieves v. Bartlett*), confirming no separate SCOTUS writing accompanied the May 18, 2026 denial in *Hedgepeth v. Britton*, No. 25-819.
