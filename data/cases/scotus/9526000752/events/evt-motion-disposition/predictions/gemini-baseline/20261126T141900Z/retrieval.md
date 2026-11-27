# Retrieval Log

Mode: `forward` (`record/context.json`: `"mode": "forward"`, `"cutoff": "2026-11-18"`).

## 1. Local CLI Inspection and Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9526000752" --event "evt-motion-disposition" --role predictor` and `uv run fedcourts query --help`
   - Confirmed predictor paths (`case_id: scotus/9526000752`, `event: data/cases/scotus/9526000752/events/evt-motion-disposition/event.yaml`), `DECIDED_BEFORE=unset`, `REPLAY_CUTOFF=unset`, and query CLI flags.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Returned 10 recent denied SCOTUS rows (including substantive application `26A729`, *Ian Buenaventura v. Leslie Buot*, plus cert denials).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Returned 10 recent granted SCOTUS rows (recent OT2026 cert grants such as `25-944`, *Robinhood Markets, Inc. v. Sodha*, and `26-289`).
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 30 | grep '"application_kind":"substantive"' | head -n 15`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from local ranged cache)
   - Returned recent resolved denied substantive applications (`26A729` *Buenaventura*, `26A686` *Overton*, `26A715` *Odom*, `26A698` *Simpkins*).
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 50 | grep '"application_kind":"substantive"' | head -n 15`
   - `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
   - Returned recent granted substantive applications (government and counseled institutional applications including `26A560` *Mullin v. Friends of the Ruidosa Church*, `26A465` *Noem v. Doe*, `26A390` *People Not Politicians*, `26A295` *NRCC v. FEC*, `25A888` *Danco Laboratories*).
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 100 | grep '"application_kind":"substantive"' | grep -i 'Seventh Circuit' | head -n 10`
   - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Returned 0 matching lines within the top 100 recent denials (dominated by October/November cert-denial order lists).
7. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 250 | grep '"application_kind":"substantive"' | grep -E 'Seventh Circuit|"ca7"' | head -n 10`
   - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Returned 0 matching lines (`--limit` capped before older Seventh Circuit applications).
8. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 200 | grep '"application_kind":"substantive"' | head -n 15`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from local ranged cache)
   - Returned 9 recent resolved substantive applications, including *pro se* non-capital applications `26A729` (*Buenaventura*), `26A698` (*Simpkins*), `26A684` (*Schultz v. BOFK*), `26A680` (*Dowden v. Deutsche Bank*), `26A658` (*Schultz v. Gold*), and `26A657` (*Schultz v. McCarthy*), all denied without a response request, full-Court referral, or *amicus* brief.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="r", docket_number="2:25-cv-01702", num_results=5, fields=["docket_id", "court_id", "caseName", "docketNumber", "dateFiled", "dateTerminated", "assignedTo"])`
   - Located originating district court RECAP docket `71870877` (`wied`, *Armstrong v. Alter Trading Corporation*, Case No. `2:25-cv-01702`, filed `2025-11-03`, assigned to Judge Joseph Peter Stadtmueller).
2. `mcp_courtlistener_search(type="r", court="ca7", docket_number="26-2488", num_results=5, fields=["docket_id", "court_id", "caseName", "docketNumber", "dateFiled", "dateTerminated"])`
   - Located originating Seventh Circuit RECAP docket `73637122` (`ca7`, *William Armstrong, III v. Alter Trading Corporation*, Case No. `26-2488`).
3. `mcp_courtlistener_search(type="o", case_name="Armstrong v. Alter Trading", num_results=5, fields=["id", "cluster_id", "court_id", "caseName", "dateFiled", "docketNumber", "citation"])`
   - Returned 0 indexed opinions in the CourtListener opinions collection.
4. `mcp_courtlistener_search(type="rd", court="wied", docket_number="2:25-cv-01702", order_by="entry_date_filed asc", num_results=30, fields=["id", "docket_id", "document_number", "attachment_number", "entry_date_filed", "description", "is_available"])`
   - Returned all 25 RECAP document entries on E.D. Wis. No. `2:25-cv-01702` (`Dkt. 1` through `Dkt. 20`, Nov. 3, 2025 – Aug. 18, 2026), identifying available screening/dismissal orders `Dkt. 10` (`id: 478834908`) and `Dkt. 12` (`id: 480922795`).
5. `mcp_courtlistener_search(type="rd", court="ca7", docket_number="26-2488", order_by="entry_date_filed asc", num_results=30, fields=["id", "docket_id", "document_number", "attachment_number", "entry_date_filed", "description", "is_available"])`
   - Returned all 25 RECAP docket entries on Seventh Circuit No. `26-2488` (`Dkt. 1` through `Dkt. 25`, July 16, 2026 – Nov. 24, 2026), including notice of non-service of appellees below (`Dkt. 2`), the Nov. 20 emergency motion to suspend the fee deadline pending Supreme Court review (`Dkt. 22`), the Nov. 24 denial order (`Dkt. 23`, `id: 502657438`), the Nov. 24 notice that the $605 appeal docketing fee was paid (`Dkt. 24`), and the Nov. 24 order advancing the fully briefed appeal to a merits disposition (`Dkt. 25`, `id: 502707895`).
6. `mcp_courtlistener_read_document(recap_document_id=480922795)`
   - Read full plain text (20,957 chars) of E.D. Wis. `Dkt. 12` (May 29, 2026 Order by Judge J.P. Stadtmueller dismissing the action with prejudice, declining contempt, and imposing a $500 sanction and *Mack* filing bar with carve-outs).
7. `mcp_courtlistener_read_document(recap_document_id=478834908)`
   - Read full plain text (21,477 chars) of E.D. Wis. `Dkt. 10` (May 11, 2026 Second Screening Order by Judge J.P. Stadtmueller detailing Rule 8 deficiencies and granting final leave to amend within 15-page / 10-defendant bounds).
8. `mcp_courtlistener_read_document(recap_document_id=502657438)`
   - Read full plain text (1,342 chars) of Seventh Circuit `Dkt. 23` (Nov. 24, 2026 Order denying emergency motion to suspend fee deadlines pending Supreme Court review and appoint counsel).
9. `mcp_courtlistener_read_document(recap_document_id=502707895)`
   - Read full plain text (1,452 chars) of Seventh Circuit `Dkt. 25` (Nov. 24, 2026 Order confirming payment of appellate filing fees and stating that briefing is complete and the appeal will proceed to a disposition on the merits).

## 3. Web Searches

None attempted.
