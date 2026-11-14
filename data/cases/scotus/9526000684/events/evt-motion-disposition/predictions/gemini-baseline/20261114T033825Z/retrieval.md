# Retrieval Log — `scotus/9526000684` (`evt-motion-disposition`)

Mode: `forward` (`DECIDED_BEFORE` unset). No query was made for this case's own disposition (`26A684` / `scotus/9526000684`), live Supreme Court docket, or any external forecast.

## 1. `fedcourts` CLI Calls

1. **Path resolution and CLI help check:**
   - `uv run fedcourts paths --court "scotus" --docket "9526000684" --event "evt-motion-disposition" --role predictor`
     - Returned `case_id scotus/9526000684`, `corpus corpus/corpus.db`, `event data/cases/scotus/9526000684/events/evt-motion-disposition/event.yaml`.
   - `uv run fedcourts query --help`
     - Returned structured filter documentation (no corpus reads).

2. **Recent resolved SCOTUS denied priors (2020s):**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 11 GET(s), 2818048 byte(s)`
   - Result: 10 resolved SCOTUS rows, including substantive emergency applications `26A661` (*Pavatt v. Oklahoma*, denied `2026-11-12`), `26A658` (*Paul Schultz v. H. Jason Gold*, `scotus/9526000658`, filed `2026-11-06`, denied `2026-11-11`), and `26A657` (*Paul Schultz v. Kevin McCarthy*, `scotus/9526000657`, filed `2026-11-06`, denied `2026-11-10`).

3. **Recent resolved SCOTUS granted priors (2020s):**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   - Result: 10 resolved SCOTUS rows, including substantive stay grants `26A560` (*Mullin v. Friends of the Ruidosa Church*, decided `2026-11-09`), `26A512` (*Scanlan v. Coalition for Open Democracy*, decided `2026-10-22`), and `26A476` (*FCC v. Brown*, decided `2026-10-14`).

4. **Attempted party filter (usage error — unsupported flag):**
   - Command: `uv run fedcourts query --court scotus --party "Paul Schultz" --decided-before 2026-11-12 --limit 20`
   - Transfer line: none (CLI usage error exit code 2: `No such option: --party`).

5. **Attempted originating-court filter (usage error — unsupported flag):**
   - Command: `uv run fedcourts query --court scotus --originating-court ca4 --era 2020s --disposition granted --limit 15`
   - Transfer line: none (CLI usage error exit code 2: `No such option: --originating-court`).

6. **Resolved denied SCOTUS applications before `2026-11-12` (`--include-applications`):**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --decided-before 2026-11-12 --limit 15`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)` (with `note: replay cutoff 2026-11-12 (from --decided-before)`).
   - Result: 15 resolved denied SCOTUS rows decided through `2026-11-11`, led by `26A658` and `26A657`.

7. **Resolved granted SCOTUS applications before `2026-11-12` (`--include-applications`):**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --include-applications --decided-before 2026-11-12 --limit 15`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)` (with `note: replay cutoff 2026-11-12 (from --decided-before)`).
   - Result: 15 resolved granted rows through `2026-11-11` (predominantly `application_kind: "extension"` plus substantive grant `26A560` and cert grant `25-1408`).

8. **Full hydration check on companion applications `26A657` and `26A658`:**
   - Command 1: `uv run fedcourts query --court scotus --docket-number 26A657 --decided-before 2026-11-12 --full`
     - Transfer line: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
     - Result: 1 row (`scotus/9526000657`, `has_opinion: false`, `opinion_text: null`, `interim_reading: "denied"`, `referred_to_court: false`, `response_requested: false`).
   - Command 2: `uv run fedcourts query --court scotus --docket-number 26A658 --decided-before 2026-11-12 --full`
     - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
     - Result: 1 row (`scotus/9526000658`, `has_opinion: false`, `opinion_text: null`, `interim_reading: "denied"`, `referred_to_court: false`, `response_requested: false`).

9. **Verification of cited SCOTUS emergency application `25A914` (*Malliotakis v. Williams*):**
   - Command: `uv run fedcourts query --court scotus --docket-number 25A914 --decided-before 2026-11-12`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: 1 row (`scotus/72353169`, `Malliotakis v. Williams`, decided `2026-03-02`, `interim_reading: "granted"`, `response_requested: true`, `referred_to_court: true`, `amicus_briefs: 2`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `docket_number="26-2405"`, `fields=["caseName", "docketNumber", "docket_id", "cluster_id", "dateFiled", "status"]`):
   - Returned `count: 0` (the unpublished October 22, 2026 mandamus opinion in CA4 No. `26-2405` was not indexed in CourtListener opinions).
2. `mcp_courtlistener_search` (`type="d"`, `docket_number="1:26-cv-01125"`, `fields=["caseName", "court_id", "docketNumber", "docket_id", "dateFiled", "dateTerminated"]`):
   - Returned `count: 24` across district courts, including E.D. Va. (`vaed`) docket `73338626`, *Schultz v. BOKF, N.A.*, filed `2026-04-27` (`dateTerminated: null`), confirming Respondent's spelling `"BOKF, N.A."`.
3. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `query={"docket": 73338626, "fields": ["entry_number", "date_filed", "description"]}`, `num_results=30`):
   - Returned `results: []` (no RECAP docket entries captured for `vaed` docket `73338626`).
4. `mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `q=""Paul Schultz""`, `fields=["caseName", "docketNumber", "dateFiled", "citation", "status"]`):
   - Returned `count: 1` (*Short v. Schultz*, 298 F. App'x 246, No. 08-6872, Nov. 5, 2008 — unrelated historical case).
5. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Clark v. Sweeney" OR "Margolin""`, `fields=["caseName", "docketNumber", "dateFiled", "citation"]`):
   - Returned `count: 166`, led by *Clark v. Sweeney*, No. `25-52` (decided `2025-11-24`).
6. `mcp_courtlistener_search` (`type="rd"`, `court="vaed"`, `docket_number="1:26-cv-01125"`, `fields=["caseName", "docketNumber", "entry_date_filed", "entry_number", "short_description", "description"]`):
   - Returned `count: 0`.
7. `mcp_courtlistener_search` (`type="rd"`, `court="vaeb"`, `docket_number="24-11959"`, `order_by="entry_date_filed desc"`, `num_results=15`, `fields=["caseName", "docketNumber", "entry_date_filed", "entry_number", "short_description", "description"]`):
   - Returned `count: 836` RECAP document entries in Bankr. E.D. Va. No. `24-11959`, confirming `entry_number: 830` (`2026-10-22`, `"Stay"`), `entry_number: 833` (`2026-10-29`, `"Order on Motion to Stay"`), `"Hearing Cancelled"` (`2026-10-29`), and `entry_number: 823–827` (`2026-08-31`, `"Transmittal of Record on Appeal to Appellate Court"`).
8. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="dockets"`, `item_id=73338626`, `fields=["id", "case_name", "docket_number", "date_filed", "date_terminated", "assigned_to_str", "referred_to_str", "cause", "nature_of_suit"]`):
   - Returned *Schultz v. BOKF, N.A.*, `1:26-cv-01125`, `assigned_to_str: "Leonie M. Brinkema"`, `referred_to_str: "Ivan D. Davis"`, `date_filed: "2026-04-27"`, `date_terminated: null`.
9. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="25-767"`, `fields=["caseName", "docketNumber", "dateFiled", "cluster_id", "opinions"]`):
   - Returned `count: 1`: *Margolin v. NAIJ*, No. `25-767` (per curiam opinion decided `2026-05-26`, 608 U.S. ___).
10. `mcp_courtlistener_search` (`type="d"`, `court="ca4"`, `party_name="Paul Schultz"`, `fields=["caseName", "docketNumber", "dateFiled", "dateTerminated", "docket_id"]`):
    - Returned `count: 20` Fourth Circuit dockets involving Paul Schultz (`25-2195` through `26-2180`, naming Clear Sky Financial, LLC, Kevin McCarthy, Matthew Cheney, Martin Law Group, P.C., and H. Gold).
11. `mcp_courtlistener_search` (`type="rd"`, `court="vaeb"`, `docket_number="24-11959"`, `q=""625" OR "833" OR "BOKF""`, `num_results=10`, `fields=["id", "is_available", "entry_date_filed", "entry_number", "short_description", "description"]`):
    - Returned `count: 1`: `entry_number: 43` (`2024-11-25`), Notice of Appearance by M. Christine Maggard of Brock & Scott, PLLC on behalf of BOKF, N.A. (`is_available: false`).

## 3. Web Searches

None.
