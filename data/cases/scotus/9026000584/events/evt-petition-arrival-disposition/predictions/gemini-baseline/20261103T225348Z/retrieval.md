# Retrieval Log

## 1. Corpus Lookups (`fedcourts query`)

1. **Command:** `uv run fedcourts query --court scotus --docket-number 25-107`
   - **Transfer line:** `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - **Result:** Returned 1 row (`scotus/73274790`, *Leah Gilliam v. David Gerregano, Commissioner, Tennessee Department of Revenue, et al.*, No. 25-107, filed 2025-07-29, distributed 2025-12-05 with `distribution_count: 2`, certiorari denied 2025-12-08, with 5 amicus briefs).

2. **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - **Transfer line:** `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - **Result:** Returned 5 recent granted SCOTUS priors from the 2020s era (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`).

## 2. CourtListener MCP Lookups

1. **Tool:** `mcp_courtlistener_search` (RECAP search, `type="r"`, `court="ca7"`, `docket_number="26-1043"`, `fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id"]`)
   - **Result:** Returned 1 match (`M J Nichols Company, Inc. v. Kristina Boardman`, 7th Cir. No. 26-1043, `docket_id: 73196733`, filed 2026-01-12).

2. **Tool:** `mcp_courtlistener_search` (Opinion search, `type="o"`, `court="ca7"`, `case_name="Nichols v. Boardman"`, `fields=["caseName", "docketNumber", "dateFiled", "citation", "cluster_id"]`)
   - **Result:** Returned 0 matches (`count: 0`), confirming that the Seventh Circuit had not yet issued an opinion in *M J Nichols Co. v. Boardman* as of prediction time.

## 3. Web Searches

- None attempted.
