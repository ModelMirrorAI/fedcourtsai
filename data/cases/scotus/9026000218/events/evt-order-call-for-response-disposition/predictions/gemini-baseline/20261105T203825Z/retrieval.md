# Retrieval Log

## 1. Corpus Tooling (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000218" --event "evt-order-call-for-response-disposition" --role predictor`
   - Transfer line: none (resolved local paths for `scotus/9026000218`).
2. `uv run fedcourts query --help`
   - Transfer line: none (CLI help output).
3. `uv run fedcourts query --court scotus --citation "514 U.S. 419" --citation "565 U.S. 73" --citation "577 U.S. 385" --citation "607 U.S. 213" --limit 10`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Empty result with coverage note explaining that only 200 SCOTUS rows carry reporter citations in the `citations` column and recommending `--court` / `--disposition` / `--era` or `--docket-number` for corpus priors and CourtListener MCP for known case citations.
4. `uv run fedcourts query --court scotus --docket-number 25-1`
   - Transfer line: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned 1 row: `scotus/73110505` (*James Skinner v. Louisiana*, No. 25-1, originating from the Supreme Court of Louisiana, distributed 9 times, cert denied `2026-03-30`, with amicus briefs by Innocence Network, Cato Institute, Patrick O'Neal, et al.).
5. `uv run fedcourts query --court scotus --docket-number 22-77`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row: `scotus/67123792` (*David Brown v. Louisiana*, No. 22-77, capital case originating from the Supreme Court of Louisiana, distributed 7 times, cert denied `2023-04-03`).
6. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS `granted` dockets (`26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, `26-104`).
7. `uv run fedcourts query --court scotus --attorney "Jorge Benjamin Aguinaga" --limit 10`
   - Transfer line: none (CLI usage error: `No such option: --attorney`).
8. `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 10`
   - Transfer line: `ranged corpus reads: 958 GET(s), 250937344 byte(s)`
   - Result: Returned 0 rows labeled `summary-reversal` in the 2020s SCOTUS slice.
9. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS `gvr` dockets (`25-1269`, `25-1367`, `25-7569`, `26-139`, `26-5216`, `25-901`, `25-918`, `25-7462`, `25-7532`, `26-48`).

## 2. CourtListener MCP Server Calls

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Brown v. Louisiana"`)
   - Result: Returned 22 historical SCOTUS entries matching "Brown v. Louisiana".
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Wearry v. Cain"`)
   - Result: Returned 1 cluster (`cluster_id: 3180088`, *Wearry v. Cain*, 577 U.S. 385 (2016), No. 14-10008, per curiam summary reversal).
3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `citation="143 S. Ct. 886"`)
   - Result: Returned 0 results.
4. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Klein v. Martin"`)
   - Result: Returned 1 cluster (`cluster_id: 10779476`, `opinion_id: 11246089`, *Klein v. Martin*, No. 25-51, decided Jan. 26, 2026).
5. `mcp_courtlistener_read_document` (`opinion_id=11246089`)
   - Result: Read full text (31,498 chars) of *Klein v. Martin*, 607 U.S. 213 (Jan. 26, 2026) (per curiam), reversing the Fourth Circuit's grant of habeas relief on a *Brady* materiality claim and explaining why a state appellate court that recites the *Brady* materiality rule and relies on strong remaining evidence linking the defendant to the crime has not covertly applied a forbidden sufficiency-of-the-evidence test under *Kyles v. Whitley*.
6. `mcp_courtlistener_search` (`type="o"`, `docket_number="22-77"`)
   - Result: Returned 47 state/lower-court opinions with docket number `22-77`.
7. `mcp_courtlistener_search` (`type="o"`, `docket_number="25-1"`)
   - Result: Returned 102 state/lower-court opinions with docket number `25-1`.
8. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="22-77"`)
   - Result: Returned 0 results.
9. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="25-1"`)
   - Result: Returned 0 results.
10. `mcp_courtlistener_search` (`type="o"`, `case_name="Robinson v. Vannoy"`)
    - Result: Returned 8 results, including *State ex rel. Darrell J. Robinson v. Vannoy*, No. 2021-KP-00812 (La. Jan. 26, 2024) (`cluster_id: 9487158`).
11. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Robinson v. Louisiana"`, `filed_after="2024-01-01"`)
    - Result: Returned 0 results.
12. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""David Brown" "Kyles" Louisiana"`)
    - Result: Returned 0 results.
13. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2026-01-01"`, `q="Skinner Louisiana"`)
    - Result: Returned 2 results (*T. M. v. University of Md. Medical System Corp.*, No. 25-197).
14. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=9487158`)
    - Result: Returned cluster metadata for *State ex rel. Darrell J. Robinson v. Vannoy* (`date_filed: "2024-01-26"`).

## 3. Web Searches
None attempted.
