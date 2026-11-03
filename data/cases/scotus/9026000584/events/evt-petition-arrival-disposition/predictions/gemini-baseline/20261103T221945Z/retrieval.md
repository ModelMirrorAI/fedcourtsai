# Retrieval Log

## 1. Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-107`
   - Transfer line: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - Result: Returned 1 row — `scotus/73274790`, *Leah Gilliam v. David Gerregano, Commissioner, Tennessee Department of Revenue, et al.*, Docket No. 25-107, filed 2025-07-29, distributed 2025-12-05 (`distribution_count: 2`), `disposition: "denied"` on 2025-12-08.

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
   - Result: Returned 10 recent OT2025/OT2026 granted rows for comparison of current-Term grant profiles and distribution counts.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="d", case_name="Nichols v. Boardman")`
   - Result: 1 docket match — *M J Nichols Company, Inc. v. Kristina Boardman*, No. 26-1043 (7th Cir., `docket_id: 73196733`), filed 2026-01-12, argued 2026-09-17, `dateTerminated: null` (still pending decision in the Seventh Circuit).

2. `mcp_courtlistener_search(type="o", case_name="Whateley v. Lackey")`
   - Result: 1 opinion cluster match — *Curtis Whateley v. Gerald Lackey*, No. 25-1751 (4th Cir., `cluster_id: 10938011`, `opinion_id: 11405587`), argued 2026-05-06, decided 2026-07-31, published.

3. `mcp_courtlistener_search(type="o", case_name="Nichols v. Boardman")`
   - Result: 0 opinion matches (confirming the Seventh Circuit has not yet issued an opinion in No. 26-1043).
