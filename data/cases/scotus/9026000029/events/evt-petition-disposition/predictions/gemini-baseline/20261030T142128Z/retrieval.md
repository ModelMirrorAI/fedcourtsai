# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 24 GET(s), 6291456 byte(s)`
   - Returned: 10 recent granted SCOTUS rows from the 2020s era (OT 2025 / OT 2026 petitions and applications) for general context on recent grant activity and salience bands.

2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned: 10 recent denied SCOTUS rows from the 2020s era for general context on recent denials.

3. `uv run fedcourts query --court scotus --citation "592 U.S. 351" --citation "581 U.S. 150" --limit 5`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned: 0 rows (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Toles v. Mead Johnson")`
   - Returned: 1 match (`Toles v. Mead Johnson & Company, LLC.`, `2025 IL App (5th) 231205`, cluster ID `10754616`, filed `2025-12-11`, `citeCount: 1`), confirming the published Illinois Appellate Court Fifth District opinion reproduced in `record/documents/appendix.txt`.

2. `mcp_courtlistener_search(type="o", case_name="Harden v. Mead Johnson")`
   - Returned: 0 matches in the indexed opinion collection (the unpublished N.D. Ill. order `2024 WL 2882214` is discussed in `petition.txt` and `appendix.txt`).
