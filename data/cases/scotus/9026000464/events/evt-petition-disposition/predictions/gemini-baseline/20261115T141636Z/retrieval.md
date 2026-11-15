# Retrieval Log

Mode: `forward` (`DECIDED_BEFORE` unset; `record/context.json` `mode: "forward"`). No forecasts, commentary odds, or `data/qp-topics/` paths were queried or read.

## 1. Corpus CLI (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000464" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Local path/help inspection; no corpus reads.
2. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer stderr: `ranged corpus reads: 9 GET(s), 2293760 byte(s)`
   - Returned 10 recent 2020s resolved SCOTUS dockets (including OT2026 grants *Robinhood Markets, Inc. v. Sodha*, No. 25-944, and *Mullin v. RAICES*, No. 26-239; GVRs *Roybal v. Griffith*, No. 25-442, and *Harrington v. Martin*, No. 25-1348; and recent cert/application denials), confirming the multi-distribution, amicus-supported, or federal-petitioner profile of granted OT2026 petitions.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer stderr: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
   - Returned 10 recent 2020s granted SCOTUS petitions and applications (*Robinhood Markets*, *Mullin v. RAICES*, *Goldman Sachs Bank USA v. Brown*, *Association for Education Fairness*, *DOJ v. McNutt*, *U.S. DOGE Service*, *Berry v. United States*, and three substantive applications), all showing multiple distributions, CVSG/SG petitioner status, or substantial amicus participation.
4. `uv run fedcourts query --court scotus --era 2020s --party "Secretary of the Army" --limit 10`
   - Failed (`Exit Code: 2`, `No such option: --party`); printed `fedcourts query` structured flag summary; 0 corpus reads.

## 2. CourtListener MCP (`courtlistener`)

1. `mcp_courtlistener_search(type="o", q='"differing site condition" "52.236-2"', fields=["caseName", "court_id", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=10)`
   - Returned `count: 116` (`query_id: "fee5571a"`), dominated by Federal Circuit and Court of Federal Claims decisions (e.g., *Nova Group/Tutor-Saliba v. United States*, 87 F.4th 1375 (Fed. Cir. 2023)), confirming exclusive CAFC/COFC doctrinal concentration.
2. `mcp_courtlistener_search(type="o", court="scotus", q='"differing site" OR "52.236-2" OR "changed conditions"', fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=10)`
   - Returned `count: 130` (`query_id: "2d40cd00"`), matching unrelated uses of `"changed conditions"` (e.g., *Kucana v. Holder*); confirmed zero Supreme Court opinions interpreting FAR 52.236-2.
3. `mcp_courtlistener_search(type="o", court="scotus", q='"Armed Services Board of Contract Appeals" OR "52.236-2" OR "7107"', fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=10)`
   - Returned `count: 79` (`query_id: "eec1cc25"`), primarily matching docket numbers containing `7107` on order lists.
4. `mcp_courtlistener_search(type="o", court="cafc", q='"Type I differing site condition" "52.236-2"', fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=10)`
   - Returned `count: 7` (`query_id: "daff8d16"`), showing settled Federal Circuit Type I differing site condition precedent through *Nova Group/Tutor-Saliba*, 87 F.4th 1375, with no intra-circuit split.
5. `mcp_courtlistener_search(type="o", court="scotus", q='"Armed Services Board of Contract Appeals"', fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=10)`
   - Returned `count: 4` (`query_id: "07428d64"`): only four Supreme Court opinions in history mention the ASBCA, the most recent on May 3, 1976 (*United States v. Testan*, 424 U.S. 392 (1976), alongside 1966–1967 Wunderlich Act cases such as *United States v. Anthony Grace & Sons, Inc.*).
6. `mcp_courtlistener_search(type="o", court="scotus", q='"Secretary of the Army"', order_by="dateFiled desc", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id"], num_results=10)`
   - Returned `count: 430` (`query_id: "48e9abcd"`), consisting overwhelmingly of routine order-list cert denials in cases naming the Secretary of the Army.

## 3. Web Retrieval (`web_fetch`)

1. `web_fetch` on `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-464.html`
   - Verified the live official Supreme Court docket for No. 26-464 in forward mode. Confirmed identical state to provisioned snapshot `2026-11-15.json` (Petition filed Sep 28, 2026; Waiver of Acting Secretary of the Army filed Nov 2, 2026; Distributed Nov 10, 2026 for Conference of 12/4/2026; no subsequent entries).
