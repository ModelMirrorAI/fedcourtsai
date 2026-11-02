# Retrieval Log (`scotus/9026000193` / `evt-petition-disposition` / `20261102T130502Z`)

## 1. Corpus CLI Queries (`uv run fedcourts query`)

1. **Companion docket lookup (`26-240`)**:
   - Command: `uv run fedcourts query --court scotus --docket-number "26-240"`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned 1 open row (`scotus/9026000240`, *Cameron Johnson, et al. v. A. Scott Fleming, Director of the State Council of Higher Education for Virginia, et al.*, docketed 2026-08-25, originating court `ca4` docket `26-1437`, distributed for conference `2026-10-16`, `distribution_count: 1`).

2. **Recent 2020s SCOTUS granted priors**:
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Result: Returned 10 recent OT2026 granted petitions and applications (including `26-12`, `26-204`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, `26-104`) showing typical distribution counts and counsel/amicus profiles for granted cert petitions.

3. **Attempted query with unsupported flags (`--originating-court` / `--attorney`)**:
   - Command: `uv run fedcourts query --court scotus --originating-court ca4 --era 2020s --disposition granted --limit 10 && uv run fedcourts query --court scotus --attorney "John J. Bursch" --limit 10 && uv run fedcourts query --court scotus --attorney "James A. Campbell" --limit 10`
   - Transfer: None (CLI usage error: `No such option: --originating-court`).

4. **Recent 2020s SCOTUS denied priors**:
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent denied SCOTUS rows from warm cache.

## 2. CourtListener MCP Calls

1. **`mcp_courtlistener_search` (Opinion search)**:
   - Parameters: `type="o"`, `court="ca4"`, `case_name="Johnson v. Fleming"`
   - Result: Returned 4 older unrelated Fourth Circuit opinions (no opinion yet in *Cameron Johnson v. Fleming* because the appeal is still pending).

2. **`mcp_courtlistener_search` (Docket search by docket number)**:
   - Parameters: `type="d"`, `docket_number="26-1437"`
   - Result: Returned 133 dockets across federal courts matching `26-1437`.

3. **`mcp_courtlistener_search` (Docket search by case name)**:
   - Parameters: `type="d"`, `case_name="Johnson v. Fleming"`
   - Result: Returned 61 dockets, including E.D. Va. Docket `3:25-cv-00407` (`id: 70392131`, *Johnson v. Fleming*, filed 2025-05-28) and Fourth Circuit Docket `26-1437` (`id: 73188902`, *Cameron Johnson v. A. Fleming*, filed 2026-04-09).

4. **`mcp_courtlistener_search` (Docket search by party name)**:
   - Parameters: `type="d"`, `party_name="Cameron Johnson"`
   - Result: Confirmed E.D. Va. (`id: 70392131`) and Fourth Circuit (`id: 73188902`) dockets for *Cameron Johnson v. A. Scott Fleming*.

5. **`mcp_courtlistener_call_endpoint` (`docket-entries` for E.D. Va. docket `70392131`)**:
   - Parameters: `endpoint_id="docket-entries"`, `query={"docket": 70392131, "fields": ["id", "date_filed", "entry_number", "description", "recap_documents"]}`
   - Result: Returned district court docket entries showing complaint and preliminary injunction motion filed May 28, 2025.

6. **`mcp_courtlistener_call_endpoint` (`docket-entries` for Fourth Circuit docket `73188902`)**:
   - Parameters: `endpoint_id="docket-entries"`, `query={"docket": 73188902, "fields": ["id", "date_filed", "entry_number", "description", "recap_documents"]}`
   - Result: Returned Fourth Circuit docket entries through Entry 73 (filed 2026-10-26), including appellants' motion to submit on the briefs (Doc. 56, confirming *Johnson v. Fleming*, No. 26-240 is a petition for writ of certiorari before judgment from the E.D. Va.'s March 31, 2026 order), appellees' opposition (Doc. 69), the Fourth Circuit's Sept. 28, 2026 order deferring the motion to submit on the briefs (Doc. 70), and Entry 73 (Oct. 26, 2026) tentatively calendaring *Johnson v. Fleming* for oral argument during the January 26–29, 2027 session.

## 3. Web Searches

- None attempted.
