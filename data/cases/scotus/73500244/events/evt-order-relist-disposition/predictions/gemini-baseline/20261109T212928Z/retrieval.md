# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-7371`
   - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned 1 row (`scotus/73338271`, *Travis McMichael v. United States*, No. 25-7371), showing `distributed_for_conference: "2026-10-16"`, `distribution_count: 1`, `date_cert_denied: "2026-10-19"`, `disposition: "denied"`.
2. `uv run fedcourts query --court scotus --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Result: Returned 10 recently granted OT2025/OT2026 SCOTUS dockets and applications for context on conference distributions and grant timing.
3. `uv run fedcourts query --court scotus --include-open --limit 30`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 20 SCOTUS rows resolved on 2026-11-09 from the 2026-11-06 conference (GVRs and denials).
4. `uv run fedcourts query --court ca11 --judge Luck --judge Black --judge Wilson --limit 5`
   - Transfer line: `ranged corpus reads: 50 GET(s), 13107200 byte(s)`
   - Result: Returned 0 rows (circuit-slice judge lists are withheld).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `court="ca10"`, `case_name="United States v. Chavarria"`)
   - Result: Returned 1 cluster (`cluster_id: 10611805`, `opinion_id: 11071905`, *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. June 16, 2025)).
2. `mcp_courtlistener_search` (`type="o"`, `court="ca11"`, `case_name="United States v. Bryan"`)
   - Result: Returned 21 results including `cluster_id: 10735802`, `opinion_id: 11203410`, *United States v. William Bryan*, 159 F.4th 1274 (11th Cir. Nov. 13, 2025).
3. `mcp_courtlistener_read_document` (`opinion_id=11071905`, `chunk_index=0`, `chunk_size=12000`)
   - Result: Read opening section of the Tenth Circuit's opinion in *United States v. Chavarria*, 140 F.4th 1257 (10th Cir. 2025).
4. `mcp_courtlistener_search_document` (`opinion_id=11203410`, `query="instrumentality"`, `snippet_size=500`)
   - Result: Returned 20 snippets (of 36 matches) from the Eleventh Circuit's opinion and dissent in *United States v. Bryan*, 159 F.4th 1274 (11th Cir. 2025).
5. `mcp_courtlistener_read_document` (`opinion_id=11071905`, `chunk_index=[3, 4]`, `chunk_size=12000`)
   - Result: Read the Commerce Clause and constitutional-avoidance analysis and dissent in *United States v. Chavarria*.
6. `mcp_courtlistener_read_document` (`opinion_id=11203410`, `chunk_index=11`, `chunk_size=12000`)
   - Result: Read the conclusion of Judge Rosenbaum's partial dissent on the § 1201(a)(1) instrumentality issue in *United States v. Bryan*.

## 3. Web Searches

- None.
