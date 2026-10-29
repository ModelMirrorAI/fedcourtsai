# Retrieval Log

## 1. Corpus Tooling (`uv run fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 9026000029 --event evt-order-call-for-response-disposition --role predictor`
   - Output: resolved `case_id` (`scotus/9026000029`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts query --help`
   - Output: CLI usage and available filter flags.
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 34 GET(s), 8847360 byte(s)`
   - Output: 10 recent 2020s SCOTUS granted petitions and substantive applications.
4. `uv run fedcourts query --court scotus --qp-text "personal jurisdiction" --limit 15`
   - Output: Rejected with CLI usage error (`No such option: --qp-text`).
5. `uv run fedcourts query --court scotus --party "Mead Johnson" --limit 10`
   - Output: Rejected with CLI usage error (`No such option: --party`).
6. `uv run fedcourts query --court scotus --docket-number "26-29" --include-open`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Output: Returned the corpus index record for `scotus/9026000029` (*Mead Johnson & Company, LLC, et al. v. Clarissa Greear, et al.*, docket `26-29`).

## 2. CourtListener MCP Server Calls

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Mallory v. Norfolk Southern", fields=["caseName", "dateFiled", "citation", "cluster_id"])`
   - Output: Returned 4 cluster results for *Mallory v. Norfolk Southern R. Co.*, 600 U.S. 122 (2023).
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Fuld v. Palestine Liberation Organization", fields=["caseName", "dateFiled", "citation", "cluster_id"])`
   - Output: Returned 2 cluster results for *Fuld v. Palestine Liberation Organization*, 606 U.S. 1 (2025).
3. `mcp_courtlistener_search(type="o", q=""Toles v. Mead Johnson" OR "Greear" "Mead Johnson"")`
   - Output: Returned 20 opinion results, including *Watson v. Mead Johnson & Co., LLC*, 2026 IL App (5th) 240936 (opinion_id `11341923`, decided June 18, 2026, reversing and remanding a $60M St. Clair County NEC verdict for a new trial) and *Abdullah v. Mead Johnson & Co., LLC*, No. 23-2905 (7th Cir. July 20, 2026, opinion_id `11403483`, MDL No. 3026 appeal).
4. `mcp_courtlistener_read_document(opinion_id=11341923, chunk_index=0)` and `mcp_courtlistener_read_document(opinion_id=11341923, chunk_index=1)`
   - Output: Read the opening chunks of *Watson v. Mead Johnson & Co., LLC*, 2026 IL App (5th) 240936, for context on the St. Clair County, Illinois NEC preterm infant formula litigation.
5. `mcp_courtlistener_read_document(opinion_id=11403483, chunk_index=0)`
   - Output: Read the opening chunk of *Abdullah v. Mead Johnson & Co., LLC* (7th Cir. July 20, 2026) for context on the N.D. Ill. MDL No. 3026 NEC litigation.
6. `mcp_courtlistener_search(type="o", q=""BNSF" "at home" "principal place of business"")`
   - Output: Returned 20 federal and state personal-jurisdiction opinions applying *Daimler AG v. Bauman* and *BNSF Railway Co. v. Tyrrell* to corporate "at home" general-jurisdiction claims.
7. `mcp_courtlistener_search(type="o", q=""Bristol-Myers" "Ford Motor" "Daimler" "Mead Johnson"")`
   - Output: Returned 1 opinion (*In re Santa Fe Natural Tobacco Co. Mktg. & Sales Practices & Prods. Liab. Litig.*).
