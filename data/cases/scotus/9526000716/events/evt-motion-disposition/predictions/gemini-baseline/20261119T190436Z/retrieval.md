# Retrieval Log (`scotus/9526000716` / `evt-motion-disposition`)

Mode: `forward` (pending OT2026 interim arrival cell). No web searches were run, and no post-decision outcome or third-party forecast was sought or encountered.

## 1. Corpus CLI Lookups (`fedcourts`)

1. **Lookup linked certiorari petition `26-6187`:**
   - Command: `uv run fedcourts query --court scotus --docket-number 26-6187`
   - Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned open row `scotus/9026006187` (*Reinaldo Dennes v. Texas*, `date_filed: "2026-11-18"`, `capital_case: true`, originating from `Court of Criminal Appeals of Texas`, `WR-34,627-03`, `disposition: null`, `distribution_count: 0`).

2. **Recent 2020s SCOTUS granted and denied priors (initial 10-row sample each):**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
   - Result: Returned 10 recent granted SCOTUS dockets (including `26A560`, `26A512`, `26A476`).
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (printed inside the combined shell invocation; confirmed on subsequent cached calls below).
   - Result: Returned 10 recent denied SCOTUS dockets, including capital application `26A686` (*Thomas M. Overton v. Florida*) and non-capital application `26A698`.

3. **Filtered scan of recent denied substantive SCOTUS applications (`--limit 35`, `--limit 50`, `--limit 100`):**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 35`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 50`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 100`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   -Command with `--include-applications`: `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --limit 100`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Confirmed `26A686` (*Overton v. Florida*, `capital_case: true`, `response_requested: false`, `response_filed_at: "2026-11-17"`, `referred_to_court: true`, `amicus_briefs: 0`) and `26A698` inside the most recent 100 denied SCOTUS rows (dominated by the Nov. 16, 2026 Monday Orders List cert denials).

4. **Check `open-events` on `26A716` and `26-6187`:**
   - Command (initial attempt without docket flag): `uv run fedcourts open-events --court scotus`
   - Transfer: none (usage error: `Name the case by exactly one of --docket and --docket-number.`)
   - Command (re-issued): `uv run fedcourts open-events --court scotus --docket 9526000716`
   - Transfer: none (`open-events` prints no transfer line)
   - Result: `evt-motion-disposition`
   - Command (re-issued): `uv run fedcourts open-events --court scotus --docket-number 26-6187`
   - Transfer: none
   - Result: `evt-petition-disposition` (`scotus/9026006187`)

5. **Broader scan of 2020s denied and granted substantive capital applications (`--limit 500`, plus one refused `--limit 2000` call):**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 500` (run twice: once filtering `capital_case`, once listing all 35 substantive applications)
   - Transfer (call 1): `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Transfer (call 2): `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
   - Result: Returned 35 denied substantive OT2026 applications, including 5 capital stay applications (`26A686` *Overton v. Florida*, `26A661` *Pavatt v. Oklahoma*, `26A623` & `26A634` *Guardado v. Florida*, `26A524` *Reaves v. Florida*) — 5/5 had `referred_to_court: true`, `response_requested: false` (with voluntary `response_filed_at` populated on 5/5), and `amicus_briefs: 0`, whereas 0/26 no-response non-capital denials were referred to the full Court.
   - Command (refused over-limit attempt): `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 2000`
   - Transfer: none (service validation error: `Input should be less than or equal to 500`)
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 500`
   - Transfer: `ranged corpus reads: 252 GET(s), 66060288 byte(s)`
   - Result: Returned 15 granted 2020s substantive capital applications (`26A428`, `25A1235`, `23A1160`, `23A308`, `22A941`, `22A441`, `22A258`, `21A372`, `21A116`, `21A33`, `20A161`, `20A129`, `20A134`, `20A122`, `20A125`): 12 were State/federal applications (mostly vacating stays), 3 were private inmates (`23A1160` *Gutierrez*, `22A941` *Glossip*, `21A33` *Ramirez*), 15/15 had `referred_to_court: true`, 0/15 had `amicus_briefs > 0`, and 0/14 execution-week applications had `response_requested: true`.

6. **Check adjacent application numbers `26A715` and `26A717` for any companion Dennes stay filing:**
   - Command: `uv run fedcourts query --court scotus --docket-number 26A715`
   - Transfer: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: Unrelated non-capital application (*Rachel Beth Odom v. Oklahoma*).
   - Command: `uv run fedcourts query --court scotus --docket-number 26A717`
   - Transfer: `ranged corpus reads: 745 GET(s), 195166208 byte(s)`
   - Result: No row for `26A717` in corpus.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Dennes", num_results=20)`:
   - Returned 10 opinions, including *Dennes v. Cockrell*, 537 U.S. 1162 (2003); *Ex parte Dennes*, No. WR-34,627-02 (Tex. Crim. App. Dec. 18, 2013) (`opinion_id: 2947289`); *John Rubio and Reinaldo Dennes v. TDCJ*, No. 15-26-00200-CV (Tex. App.—15th Dist. Nov. 9, 2026); and *In re John Rubio and Reinaldo Dennes*, No. 26-1300 (Tex. Nov. 11, 2026) (`opinion_id: 11527763`).
2. `mcp_courtlistener_read_document(opinion_id=2947289, chunk_index=0)`:
   - Read TCCA's December 18, 2013 unpublished order denying relief on Dennes's second state habeas application (`WR-34,627-02`).
3. `mcp_courtlistener_read_document(opinion_id=11527763, chunk_index=0)`:
   - Read Justice Young's November 11, 2026 concurrence in the Texas Supreme Court's denial of mandamus in Dennes's separate lethal-injection pharmacy suit, confirming Dennes's scheduled November 19, 2026 execution date.
4. `mcp_courtlistener_search(type="o", q=""Reinaldo Dennes"", num_results=20)`:
   - Returned the same 3 Texas appellate/habeas opinions naming Reinaldo Dennes in full.
5. `mcp_courtlistener_search(type="r", q=""Reinaldo Dennes"", num_results=20)`:
   - Returned 2 federal RECAP habeas dockets: *Dennes v. Livingston*, No. 4:14-cv-00019 (S.D. Tex. filed Jan. 6, 2014, `docket_id: 5887303`) and *Reinaldo Dennes v. Lorie Davis, Director*, No. 17-70010 (5th Cir. filed Apr. 20, 2017, `docket_id: 4465`).
6. `mcp_courtlistener_search(type="o", court="ca5", docket_number="17-70010", num_results=10)`:
   - Returned 1 unrelated 1990 opinion (`Fairley v. Allain`) due to docket-number substring indexing; no published CA5 opinion indexed under `17-70010`.
7. `mcp_courtlistener_search(type="r", court="txsd", docket_number="4:14-cv-00019", q="memorandum OR opinion OR order OR Wiggins", num_results=10)`:
   - Located Doc. 36 (`recap_document_id: 19789042`), Judge Sim Lake's 42-page Memorandum Opinion and Order entered March 23, 2017 denying Dennes's amended § 2254 petition and denying a COA.
8. `mcp_courtlistener_read_document(recap_document_id=19789042, chunk_index=[0, 1])`:
   - Read pages 1–7 of Judge Lake's opinion setting out the TCCA direct-appeal facts of the January 24, 1996 Szucs robbery-murder and prior procedural history (`Dennes v. State`, No. 72,966, Jan. 5, 2000; `WR-34,627-02`, Dec. 18, 2013).
9. `mcp_courtlistener_search_document(recap_document_id=19789042, query="mitigat")` and `mcp_courtlistener_search_document(recap_document_id=19789042, query="ineffective")`:
   - Verified what mitigation and ineffective-assistance claims Dennes litigated in his 2014–2017 federal § 2254 proceeding.
10. `mcp_courtlistener_search(type="o", court="ca5", q=""Dennes" "Davis" OR "Dennes" "Cockrell"", num_results=10)`, `mcp_courtlistener_search(type="o", court="ca5", q=""17-70010"", num_results=10)`, and `mcp_courtlistener_search(type="o", court="ca5", q=""Szucs" "Dennes"", num_results=10)`:
    - Checked whether the Fifth Circuit's final order in `17-70010` was indexed in CourtListener opinions (0 relevant matches).
11. `mcp_courtlistener_search(type="r", court="ca5", docket_number="17-70010", num_results=10)`:
    - Confirmed Fifth Circuit docket `17-70010` (*Reinaldo Dennes v. Lorie Davis, Director*) heard argument May 15, 2019, granted COA in part May 29, 2019, and terminated January 6, 2020.

## 3. Web Searches

None.
