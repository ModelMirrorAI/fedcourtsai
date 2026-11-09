# Retrieval Log

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "73500257" --event "evt-order-relist-disposition" --role predictor`
   - Output: resolved `case_id` (`scotus/73500257`), `corpus` (`corpus/corpus.db`), and `event` path.
2. `uv run fedcourts query --help`
   - Output: printed CLI flag documentation.
3. `uv run fedcourts query --court scotus --citation "571 U.S. 3" --citation "595 U.S. 1" --citation "584 U.S. 100" --citation "594 U.S. 295" --citation "583 U.S. 48" --before 2026-11-09 --limit 25`
   - Result: usage error (`No such option: --before (Possible options: --decided-before, --era)`).
4. `uv run fedcourts query --court scotus --lower-court ca9 --topic 1 --before 2026-11-09 --limit 25`
   - Result: usage error (`No such option: --lower-court`).
5. `uv run fedcourts query --court scotus --lower-court ca9 --topic 2 --before 2026-11-09 --limit 25`
   - Result: usage error (`No such option: --lower-court`).
6. `uv run fedcourts query --court scotus --disposition summary-reversal --decided-before 2026-11-09 --limit 30`
   - Transfer line: `ranged corpus reads: 1018 GET(s), 266731520 byte(s)`
   - Result: 0 rows (summary reversals are stored under `granted` in the corpus disposition column).
7. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-11-09 --limit 30`
   - Transfer line: `ranged corpus reads: 61 GET(s), 15925248 byte(s)`
   - Result: 30 recent SCOTUS granted rows from OT2025/OT2026.
8. `uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026-11-09 --limit 30`
   - Transfer line: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Result: 30 recent SCOTUS denied rows from OT2025/OT2026.
9. `uv run fedcourts query --court scotus --citation "146 S. Ct. 926" --decided-before 2026-11-09 --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 0 rows (note on sparse `citations` column).
10. `uv run fedcourts query --court scotus --citation "595 U.S. 1" --citation "584 U.S. 100" --citation "571 U.S. 3" --decided-before 2026-11-09 --limit 10`
    - Transfer line: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
    - Result: 0 rows (note on sparse `citations` column).
11. `uv run fedcourts query --court ca9 --judge "Friedland" --judge "Mendoza" --decided-before 2026-11-09 --limit 20`
    - Transfer line: `ranged corpus reads: 135 GET(s), 35389440 byte(s)`
    - Result: 0 rows (circuit judge lists withheld).
12. `uv run fedcourts query --court scotus --docket-number "25-297" --decided-before 2026-11-09`
    - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
    - Result: 1 row (`scotus/72528904`, *Jacob P. Zorn v. Shela M. Linton*, `docket_number: "25-297"`, `distribution_count: 10`, `disposition: "granted"`, `merits_decided: "2026-03-23"`, `merits_judgment: "reversed"`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type: "o"`, `case_name: "Zorn v. Linton"`)
   - Result: returned 2 clusters (SCOTUS `cluster_id: 10813527`, `opinion_id: 11280281`, filed `2026-03-23`; and 2d Cir. `cluster_id: 10373712`, filed `2025-03-04`).
2. `mcp_courtlistener_search` (`type: "o"`, `case_name: "Case v. Montana"`)
   - Result: returned 1 cluster (SCOTUS `cluster_id: 10774335`, `opinion_id: 11240920`, filed `2026-01-14`).
3. `mcp_courtlistener_search` (`type: "o"`, `court: "scotus"`, `case_name: "Stanton v. Sims"`)
   - Result: returned 1 cluster (SCOTUS `cluster_id: 9823764`, `opinion_id: 9518678`, 571 U.S. 3, filed `2013-11-04`).
4. `mcp_courtlistener_search` (`type: "o"`, `court: "scotus"`, `case_name: "Rivas-Villegas v. Cortesluna"`)
   - Result: transient tool error (`fetch failed`).
5. `mcp_courtlistener_read_document` (`opinion_id: 11280281`)
   - Result: returned full text (42,470 chars) of *Zorn v. Linton*, 607 U.S. ___ (Mar. 23, 2026) (per curiam) (and Justice Sotomayor's dissent joined by Justices Kagan and Jackson).
6. `mcp_courtlistener_read_document` (`opinion_id: 11240920`, `chunk_index: 0`, `chunk_size: 10000`)
   - Result: returned chunk 0 of *Case v. Montana*, 607 U.S. 107 (Jan. 14, 2026).
7. `mcp_courtlistener_call_endpoint` (`endpoint_id: "dockets"`, `query: {"court": "scotus", "docket_number": "25-297", "fields": ["id", "case_name", "date_filed", "date_terminated"]}`)
   - Result: returned docket `72528904` (*Jacob P. Zorn, Petitioner v. Shela M. Linton*).
