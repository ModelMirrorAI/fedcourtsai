# Retrieval Log

## 1. `fedcourts` CLI Calls

- `uv run fedcourts paths --court "scotus" --docket "73500275" --event "evt-order-relist-disposition" --role predictor`
  - Resolved case and event paths.
- `uv run fedcourts query --help`
  - Inspected structured filter flags for `fedcourts query`.
- `uv run fedcourts query --court scotus --docket-number 25-944`
  - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
  - Result: Returned `scotus/73280982` (*Robinhood Markets, Inc., et al. v. Vinod Sodha, et al.*, No. 25-944), confirming `cvsg_date: "2026-06-01"`, United States appearance by Solicitor General D. John Sauer, `distributed_for_conference: "2026-11-13"`, `distribution_count: 3`, and `disposition: null`.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
  - Transfer line: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
  - Result: Returned 10 recent granted SCOTUS petitions/applications from the 2020s era for context on recent distribution counts and grant patterns.

## 2. CourtListener MCP Calls

- `mcp_courtlistener_search(type="o", case_name="Sodha v. Golubowski", fields=["caseName", "citation", "court_id", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
  - Result: Returned 1 match (`cluster_id: 10663157`, `opinion_id: 11129744`, Ninth Circuit docket `24-1036`, filed `2025-08-29`).
- `mcp_courtlistener_search(type="r", docket_number="25-944", fields=["caseName", "court_id", "dateFiled", "docketNumber", "docket_id"])`
  - Result: Returned 167 lower-court RECAP dockets matching `25-944` (no SCOTUS docket match, as expected for RECAP search).
- `mcp_courtlistener_read_document(opinion_id=11129744, chunk_index=[0, 1, 2, 3])`
  - Result: Read chunks 0–3 of *Sodha v. Golubowski* (summary, background, and statements at issue in Robinhood's IPO registration statement).
- `mcp_courtlistener_read_document(opinion_id=11129744, chunk_index=[6, 7, 8, 9, 10])`
  - Result: Read chunks 6–10 of *Sodha v. Golubowski* (Ninth Circuit holdings on Section 11(a)'s misleading-omission prong, rejection of the First Circuit's *Shaw* "extreme departure" test, and Item 303's disclosure standard).

## 3. Workspace Searches Beyond `record/`

- Read `data/cases/scotus/73500275/summaries/2026-10-27.md` (case-level summary file) and ran `grep_search` in `metrics/*.md` for `25-944|25-1376|Robinhood|ON24` to check whether `Robinhood` appeared in the published docket/big-cases tables (`metrics/big-cases.md` and `metrics/updates/2026-W44.md` matched; prior-event forecast numbers in those lines were disregarded). Attempted `list_directory` on `data/cases/scotus/73280982/record/snapshots` and `documents` (`ENOENT`, not staged in this cell).
