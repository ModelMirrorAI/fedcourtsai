# Retrieval Log — `scotus/9526000532` (`evt-motion-disposition`)

## 1. Corpus CLI Queries (`fedcourts`)

1. `uv run fedcourts query "Monte" --court scotus --include-applications`
   - Result: CLI usage error (positional argument rejected; no corpus read performed).
2. `uv run fedcourts query "stay" --court scotus --include-applications --limit 10`
   - Result: CLI usage error (positional argument rejected; no corpus read performed).
3. `uv run fedcourts query --court scotus --include-applications --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Retrieved 10 recent resolved SCOTUS applications (both substantive and extension) to inspect recent OT2026 interim dispositions.
4. `uv run fedcourts query --court scotus --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Retrieved 10 recent resolved SCOTUS substantive applications and cert petitions (`26A512`, `26A416`, `26A545`, `26A524`, `26A530`, `26A536`, etc.) to compare pro se vs. institutional interim stay outcomes.
5. `uv run fedcourts query --docket-number "26A532" --include-open --include-applications`
   - Result: CLI usage error (`--docket-number needs --court`; no corpus read performed).
6. `uv run fedcourts query --court scotus --docket-number "26A532" --include-open --include-applications`
   - Transfer: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Purpose: Checked the corpus metadata row for `26A532`.
7. `uv run fedcourts query --court ca3 --docket-number "26-2501" --include-open`
   - Transfer: `ranged corpus reads: 60 GET(s), 15728640 byte(s)`
   - Purpose: Checked the corpus row for the originating Third Circuit appeal (`ca3/73492184`, No. 26-2501).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="ca3"`, `case_name="Monte"`)
   - Checked for published or unpublished Third Circuit opinions matching "Monte".
2. `mcp_courtlistener_search` (`type="r"`, `case_name="Monte"`, `docket_number="26-2501"`)
   - Located Third Circuit RECAP docket `United States v. Frank Monte, III`, No. 26-2501 (`docket_id: 73492184`, filed `2026-06-16`).
3. `mcp_courtlistener_search` (`type="r"`, `case_name="Monte"`, `docket_number="26-2501"`, with `recap_documents`)
   - Retrieved initial docket entries for CA3 No. 26-2501 showing it is a criminal appeal from D.N.J. No. `3:19-cr-00821-001`.
4. `mcp_courtlistener_search` (`type="r"`, `case_name="Frank Monte"`)
   - Found related Third Circuit mandamus docket `In re: Frank Monte, III`, No. 26-2872 (`docket_id: 73670071`, filed `2026-07-24`).
5. `mcp_courtlistener_search` (`type="o"`, `case_name="Frank Monte"`)
   - Checked for opinions across all courts involving "Frank Monte".
6. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=73492184`)
   - Retrieved docket entries 1–4 in CA3 No. 26-2501, including Entry 4 (June 16, 2026 Clerk Order regarding Appellant Monte's emergency motion for stay pending appeal filed with the notice of appeal).
7. `mcp_courtlistener_search` (`type="r"`, `docket_number="19-cr-00821"`)
   - Located the originating criminal docket `United States v. MONTE`, No. 3:19-cr-00821 (D.N.J., `docket_id: 69323881` and `71069444`).
8. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=73670071`)
   - Retrieved docket entries 1–6 in CA3 No. 26-2872 (Monte's pro se mandamus petition and IFP motions).
9. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=69323881`)
   - Retrieved recent docket entries (up to Entry 318) in D.N.J. No. 3:19-cr-00821.
10. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=71069444`)
    - Checked secondary D.N.J. docket record (0 entries returned).
11. `mcp_courtlistener_search` (`type="o"`, `q=""Frank Michael Monte" OR "3:19-cr-00821" OR "19-cr-821""`)
    - Checked opinion index for district court criminal docket number (0 results).
12. `mcp_courtlistener_search` (`type="rd"`, `q=""Frank Michael Monte" OR "3:19-cr-00821" OR "19-cr-821""`)
    - Located available RECAP documents in D.N.J. No. 3:19-cr-00821, including Document 280 (`id: 423003885`, Memorandum Opinion of Dec. 6, 2024) and Document 291 (`id: 444098625`, Memorandum Opinion of June 27, 2025).
13. `mcp_courtlistener_read_document` (`recap_document_id=423003885`)
    - Read Judge Robert Kirsch's December 6, 2024 Memorandum Opinion in *United States v. Frank Michael Monte*, No. 19-cr-821 (D.N.J.), detailing Monte's 2022 conviction under 18 U.S.C. §§ 115(a)(1)(B) and 875(c), 57-month sentence, supervised release revocation proceedings, and untimeliness/mandamus issues under 28 U.S.C. § 2255.
14. `mcp_courtlistener_read_document` (`recap_document_id=444098625`)
    - Checked Document 291 (June 27, 2025 Memorandum Opinion; scanned page headers only).
15. `mcp_courtlistener_call_endpoint` (`endpoint_id="recap-documents"`, `docket_entry__docket=69323881`)
    - Listed descriptions of recent filings in D.N.J. No. 3:19-cr-00821 (Entries 289–318), showing the June 15, 2026 Notice of Appeal (Entry 307), August 12, 2026 USCA Judgment (Entry 313), and October 16, 2026 USCA Mandate terminating the appeal (Entry 316).
16. `mcp_courtlistener_search` (`type="r"`, `court="njd"`, `case_name="Monte"`)
    - Checked related D.N.J. civil actions filed by Monte.
17. `mcp_courtlistener_call_endpoint` (`endpoint_id="recap-documents"`, `docket_entry__docket=73492184`)
    - Checked document availability on CA3 docket 73492184.
18. `mcp_courtlistener_search` (`type="rd"`, `docket_number="26-2501"`) and (`type="rd"`, `docket_number="26-2872"`)
    - Checked whether any additional RECAP documents were indexed under those docket numbers.
19. `mcp_courtlistener_search` (`type="r"`, `court="ca3"`, `case_name="Monte"`)
    - Confirmed the two Third Circuit dockets (`26-2501` and `26-2872`).

## 3. Web Searches
- None performed.
