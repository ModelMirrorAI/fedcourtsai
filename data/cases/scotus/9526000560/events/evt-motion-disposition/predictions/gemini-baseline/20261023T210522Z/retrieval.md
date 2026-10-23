# Retrieval Log (`scotus/9526000560` / `evt-motion-disposition`)

## 1. Corpus CLI Lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26A124 --include-applications`
   - `ranged corpus reads: 6 GET(s), 1441792 byte(s)`
   - Retrieved `scotus/9526000124` (*Donald J. Trump, President of the United States, et al. v. California, et al.*, `26A124`, decided `2026-08-24`, `disposition: "granted"`).
2. `uv run fedcourts query --court scotus --docket-number 26A203 --include-applications`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Retrieved `scotus/9526000203` (*National Park Service, et al. v. National Trust for Historic Preservation in the United States*, `26A203`, decided `2026-08-31`, `disposition: "granted"`).
3. `uv run fedcourts query --court scotus --docket-number 26A308 --include-applications`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Retrieved `scotus/9526000308` (*Department of Homeland Security, et al. v. League of Women Voters, et al.*, `26A308`, decided `2026-09-25`, `disposition: "granted"`).
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --include-applications --limit 15`
   - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Retrieved recent granted OT2026 applications (`26A512` substantive; remainder time extensions).
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
   - `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   - Retrieved recent granted OT2026 substantive applications and cert petitions (`26A512`, `26A476` *FCC v. Brown*, `26A428`, `26A406` *DHS v. D.V.D.*, `26A308`, `26A388`).
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 25`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Retrieved recent denied OT2026 substantive applications and cert petitions (including `26A416` *Trump v. Kingdom*, decided `2026-10-21`, `disposition: "denied"`).
7. `uv run fedcourts query --court scotus --docket-number 19A60 --include-applications`
   - `ranged corpus reads: 597 GET(s), 156368896 byte(s)`
   - Checked historical rows for `19A60` (*Trump v. Sierra Club*).
8. `uv run fedcourts query --court scotus --citation "588 U.S. 930" --include-applications`
   - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Checked citation lookup coverage note.
9. `uv run fedcourts query --court scotus --docket-number 26A560 --include-applications --include-open`
   - `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Retrieved open corpus row for `scotus/9526000560` (*Mullin v. Friends of the Ruidosa Church*, `26A560`, `disposition: null`, `response_requested: true`, `response_requested_at: "2026-10-22"`, `referred_to_court: false`, `amicus_briefs: 0`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="r"`, `case_name="Friends of the Ruidosa Church v. Mullin"`):
   - Located originating district court docket `3:26-cv-01099` in the Western District of Texas (`docket_id: 73199706`, filed `2026-04-16`).
2. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="dockets"`, `item_id=73199706`):
   - Confirmed assignment to Judge Kathleen Cardone.
3. `mcp_courtlistener_search` (`type="rd"`, `docket_number="3:26-cv-01099"`):
   - Listed recent docket entries and identified Document 75 (Memorandum Opinion granting Preliminary Injunction, `recap_document_id: 497310911`), Document 77 & 77-1 (Plaintiffs' Response in Opposition to Motion to Stay Preliminary Injunction and Declaration, `recap_document_id: 498016951` and `498025102`), and Document 78 (Order Denying Motion to Stay Preliminary Injunction, `recap_document_id: 498070832`).
4. `mcp_courtlistener_read_document` (`recap_document_id=497310911`, `498070832`, `498025102`, `498016951`):
   - Read the full text of the District Court's October 14, 2026 Memorandum Opinion (14 pages), the District Court's October 20/21, 2026 Order Denying Motion to Stay Preliminary Injunction (6 pages), and Plaintiffs' October 20, 2026 Opposition to Motion to Stay Preliminary Injunction (28 pages) and attached declaration.

## 3. Web Searches

- None performed.
