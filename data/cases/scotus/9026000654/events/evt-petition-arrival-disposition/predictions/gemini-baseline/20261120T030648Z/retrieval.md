# Retrieval Log

Mode: `forward` (`record/context.json`). No queries were made for this case's own Supreme Court disposition or third-party forecasts. All calls beyond the provisioned workspace inputs are listed below in chronological order.

## 1. Corpus Lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned: 10 recent resolved 2020s SCOTUS rows (`26A686`, `26A714`, `26A715`, `26A716`, `25-1255`, `26A698`, `25-1238`, `25-1240`, `25-1303`, `25-1324`), showing `distribution_count: 0` on pre-distribution Rule 46 dismissal `25-1255` (`The Hain Celestial Group v. Gimpel`) versus `distribution_count >= 2` on conferenced cert denials.

2. `uv run fedcourts query --court scotus --citation "596 U.S. 61" --limit 5`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned: 0 rows, accompanied by the `note:` line explaining that only 195 SCOTUS rows in scope carry parallel reporter citations in the `citations` column.

3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
   - Returned: 10 recent OT2026 granted SCOTUS rows (`25-944`, `26-239`, `26A560`, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`), confirming no recently granted merits docket addresses *Reed v. Town of Gilbert*, *City of Austin*, or municipal solicitation ordinances.

4. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 15`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm local corpus cache)
   - Returned: 15 recent 2020s denied SCOTUS rows (`26A686`, `26A715`, `26A716`, `26A698`, `25-1238`, `25-1240`, `25-1303`, `25-1324`, `25-7485`, `25-7562`, `25-7667`, `26-4`, `26-62`, `26-100`, `26-120`), confirming `distribution_count >= 1` on every denied Term-form cert petition (`26-62` at `1`, others at `2–6`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court=["ca1","ca2","ca3","ca4","ca5","ca6","ca7","ca8","ca9","ca10","ca11","cadc"]`, `filed_after="2022-04-21"`, `q='"City of Austin" AND (panhandling OR "immediate donation" OR panhandle) -Daytona'`, `num_results=20`)
   - Returned: `query_id: "533bc134"`, `count: 0`, `results: []`. Confirmed no federal court of appeals decision post-*City of Austin* (other than the decision below) addresses *City of Austin* in a panhandling or immediate-donation case.

2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2015-06-18"`, `q='(panhandling OR panhandle OR "immediate donation") OR ("City of Austin" AND solicitation)'`, `num_results=20`)
   - Returned: `query_id: "81e116a5"`, `count: 10`, headed by *City of Austin v. Reagan National Advertising of Austin, LLC*, 596 U.S. 61 (2022) (`cluster_id: 6333582`, `opinion_id: 6333582`).

3. `mcp_courtlistener_search` (`type="o"`, `court="ca5"`, `filed_after="2024-01-01"`, `q='("National Federation of the Blind" AND Arlington) OR ("Rash" AND "Lafayette")'`, `num_results=10`)
   - Returned: `query_id: "f8b56ac3"`, `count: 2` — *Rash v. Lafayette County, MS* (5th Cir. May 13, 2026, `cluster_id: 10976576`, `opinion_id: 11444216`) and *National Federation of the Blind of Texas, Inc. v. City of Arlington*, 109 F.4th 728 (5th Cir. July 22, 2024, `cluster_id: 10075578`, `opinion_id: 10472191`), both cited in Petitioner's Table of Authorities.

4. `mcp_courtlistener_search` (`type="o"`, `court=["ca1","ca2","ca3","ca4","ca5","ca6","ca7","ca8","ca9","ca10","ca11","cadc"]`, `filed_after="2015-06-18"`, `q='(panhandling OR panhandle) AND "Reed v. Town of Gilbert" -Daytona'`, `num_results=25`)
   - Returned: `query_id: "b24501c2"`, `count: 1` (*Brown v. Gov't of D.C.*, 390 F. Supp. 3d 114, 2019-06-11, `cluster_id: 8344511`).

5. `mcp_courtlistener_search_document` (`opinion_id=[11444216, 10472191]`, `query="compelling"`, `snippet_size=300`)
   - Returned: 2 matches in *Rash v. Lafayette County* (`11444216`, addressing strict scrutiny and public-roadway crowd/traffic control) and 0 matches in *NFB v. City of Arlington* (`10472191`).

6. `mcp_courtlistener_search_document` (`opinion_id=[11444216, 10472191]`, `query="solicitation"`, `snippet_size=300`)
   - Returned: 0 matches in *Rash* (`11444216`) and 20 shown of 40 matches in *NFB v. City of Arlington* (`10472191`), confirming *NFB* upheld a physical unattended donation-box zoning ordinance regulating all donation receptacles regardless of signage or operator.

7. `mcp_courtlistener_search` (`type="o"`, `court=["ca1","ca2","ca3","ca4","ca5","ca6","ca7","ca8","ca9","ca10","ca11","cadc"]`, `filed_after="2015-06-18"`, `q='(panhandling OR panhandle) AND Reed -Daytona'`, `num_results=25`)
   - Returned: `query_id: "a20cd81c"`, `count: 1` (*Brown v. Gov't of D.C.*, `cluster_id: 8344511`).

8. `mcp_courtlistener_search` (`type="o"`, `court=["ndtex","cdcal"]`, `filed_after="2024-01-01"`, `q='("Arms of Hope" AND Mansfield) OR ("U'SAgain" AND "Los Angeles")'`, `num_results=10`)
   - Returned: **Failed validation error** — `ndtex` and `cdcal` were rejected as invalid court codes (`txnd` and `cacd` are the valid CourtListener identifiers).

9. `mcp_courtlistener_search` (`type="o"`, `court=["txnd","cacd"]`, `filed_after="2024-01-01"`, `q='("Arms of Hope" AND Mansfield) OR (USAgain AND "Los Angeles")'`, `num_results=10`)
   - Returned: `query_id: "8cbeb567"`, `count: 0`, `results: []` (confirming those two district-court unattended donation-bin orders cited by Petitioner are not in the published opinion index).

10. `mcp_courtlistener_search` (`type="o"`, `court=["ca3","ca7","ca8","ca10"]`, `filed_after="2015-06-18"`, `q='("Norton" AND "Springfield") OR ("Rodgers" AND "Bryant") OR ("McCraw" AND "Oklahoma City") OR ("Camp Hill" AND "Camp Hill")'`, `num_results=15`)
    - Returned: `query_id: "06975c5a"`, `count: 4` — *McCraw v. City of Oklahoma City*, 973 F.3d 1057 (10th Cir. 2020); *Camp Hill Borough Republican Ass'n v. Borough of Camp Hill*, 101 F.4th 266 (3d Cir. 2024); *Cozy Inn, Inc. v. City of Salina, Kansas* (10th Cir. Oct. 30, 2026, `opinion_id: 11518510`); and *Harmon v. City of Norman* (10th Cir. 2022).

11. `mcp_courtlistener_search_document` (`opinion_id=11518510`, `query="Austin"`, `snippet_size=300`)
    - Returned: 7 matches in *Cozy Inn, Inc. v. City of Salina, Kansas* (`11518510`), involving a municipal mural/sign distinction under *Reed* and *City of Austin*.

12. `mcp_courtlistener_search_document` (`opinion_id=11518510`, `query="solicitation"`, `snippet_size=300`)
    - Returned: 0 matches in *Cozy Inn* (`11518510`).

13. `mcp_courtlistener_search` (`type="o"`, `citation="806 F.3d 411"`, `num_results=5`)
    - Returned: `query_id: "ec89e617"`, `count: 1` — *Norton v. City of Springfield*, 806 F.3d 411 (7th Cir. 2015) (`cluster_id: 3001614`, `opinion_id: 9810191`).

14. `mcp_courtlistener_search` (`type="o"`, `citation="942 F.3d 451"`, `num_results=5`)
    - Returned: `query_id: "92c81cee"`, `count: 2` — *Rodgers v. Bryant*, 942 F.3d 451 (8th Cir. 2019) (`cluster_id: 4449635`).

15. `mcp_courtlistener_search_document` (`opinion_id=6333582`, `query="Norton"`, `snippet_size=400`)
    - Returned: 8 matches in *City of Austin*, 596 U.S. 61 (2022) (`6333582`), confirming Justice Thomas's dissent (joined by Justices Gorsuch and Barrett) cited *Norton v. City of Springfield*, 806 F.3d 411, 412 (7th Cir. 2015), with approval.

16. `mcp_courtlistener_search_document` (`opinion_id=6333582`, `query="solicitation"`, `snippet_size=400`)
    - Returned: 11 matches in *City of Austin* (`6333582`), confirming Justice Sotomayor's majority opinion stated that solicitation restrictions are content-neutral only `"so long as they do not discriminate based on topic, subject matter, or viewpoint"`.

17. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q='"Michael H. Kahn" -Daytona'`, `num_results=10`)
    - Returned: `query_id: "07c5774b"`, `count: 0`, `results: []`.

## 3. Web Searches

None attempted.
