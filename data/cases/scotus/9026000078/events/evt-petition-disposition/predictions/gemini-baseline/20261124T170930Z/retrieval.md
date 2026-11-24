# Retrieval Log

Mode: `forward` (`snapshot_date: 2026-11-24`). All lookups below sought prior precedents, companion-case context (*Jackson v. Florida*, No. 26-76, and *Kian v. Florida*, No. 25-6623), and corpus base-rate context; none queried for any post-snapshot disposition of `scotus/9026000078`.

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000078" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Result: Confirmed predictor paths (`case_id scotus/9026000078`, `event.yaml` path) and `fedcourts query` flag options. No ranged corpus reads.
2. `uv run fedcourts query --court scotus --citation "569 U.S. 530" --citation "432 U.S. 282" --citation "497 U.S. 37" --citation "529 U.S. 513" --limit 15`
   - Stderr/stats: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (printed note that `citations` holds a row's own parallel cites on 195 SCOTUS rows rather than a citing-cases graph).
3. `uv run fedcourts query --court scotus --party "Florida" --era 2020s --limit 20`
   - Result: CLI usage error (`No such option: --party`); printed supported filter flags.
4. Chained corpus lookup (single shell invocation):
   - `uv run fedcourts query --court scotus --docket-number "25-6623" --include-open`
   - `uv run fedcourts query --court scotus --docket-number "26-76" --include-open`
   - `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15`
   - Combined stderr/stats: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Results:
     - `25-6623`: Returned `scotus/73282277` (*Hamed Kian v. Florida*, noncapital appeal from Fla. 4th DCA `4D2024-2370`, `date_cert_granted: "2026-06-15"`).
     - `26-76`: Returned `scotus/9026000076` (*Michael James Jackson v. Florida*, companion capital petition from Fla. Sup. Ct. `SC2023-1298`, pending, `distributed_for_conference: "2026-12-11"`, `distribution_count: 3`).
     - `--disposition granted --era 2020s --limit 15`: Returned 15 recent SCOTUS granted rows from OT2025–OT2026 as corpus priors.
5. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 10`
   - Stderr/stats: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent OT2026 SCOTUS denied rows (including multi-distribution denials `25-1240` and `25-1324`) as corpus priors.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="d", docket_number="25-6623", fields=["caseName", "docketNumber", "docket_id", "dateFiled", "court_id"])`
   - Result: `count: 30` federal district/JPML dockets (`25-cv-06623` / `25-mj-06623`); no SCOTUS docket entry.
2. `mcp_courtlistener_search(type="d", court="scotus", case_name="Jackson v. Florida", filed_after="2026-01-01", fields=["caseName", "docketNumber", "docket_id", "dateFiled"])`
   - Result: `count: 0` (SCOTUS RECAP docket not indexed under that search).
3. `mcp_courtlistener_search(type="o", court="fla", q='"Jackson v. State" "921.141" nonunanimous OR supermajority', fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber"])`
   - Result: `count: 266`; located companion lower-court decision *Michael James Jackson v. State of Florida*, No. `SC2023-1298` (`cluster_id: 10760840` filed `2025-12-18`, corrected opinion `cluster_id: 10761718` filed `2025-12-19`).
4. `mcp_courtlistener_search(type="o", court="fladistctapp", docket_number="4D2024-2370", fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber"])`
   - Result: `count: 1`; located *Hamed Kian v. State of Florida*, No. `4D2024-2370`, `cluster_id: 10752753` (`2025-10-16`).
5. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10761718, "fields": ["id", "type", "author_str"]})`
   - Result: Returned `opinion_id: 11228303` for *Jackson v. State* (`SC2023-1298`).
6. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10752753, "fields": ["id", "type", "author_str"]})`
   - Result: Returned `opinion_id: 11219338` for *Kian v. State* (`4D2024-2370`).
7. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2023-01-01", q='"921.141" OR "Poole" OR "unanimous" Florida death', fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber"])`
   - Result: `count: 52` SCOTUS opinions (including *Whitton v. Dixon*, No. `25-580`, `cluster_id: 10867983`, `2026-06-01`, and general criminal opinions).
8. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10867983, "fields": ["id", "type", "author_str"]})`
   - Result: Returned `opinion_id: 11335438` for *Whitton v. Dixon*.
9. `mcp_courtlistener_read_document(opinion_id=11219338, chunk_index=0, chunk_size=4000)`
   - Result: Read full text (1,055 chars) of *Hamed Kian v. State of Florida* (`4D2024-2370`, per curiam affirmance).
10. `mcp_courtlistener_search_document(opinion_id=11228303, query="921.141", snippet_size=400)`
    - Result: `match_count: 22` (`shown: 20`) in *Jackson v. State* (`SC2023-1298`).
11. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2023-04-01", q='"921.141" OR "eight" "unanimous" "Florida" death', fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber"])`
    - Result: `count: 10` general SCOTUS opinions; confirmed no prior SCOTUS opinion deciding Florida's 2023 SB 450 8–4 capital sentencing amendment.
12. `mcp_courtlistener_read_document(opinion_id=11228303, chunk_index=[4, 5, 6], chunk_size=8000)`
    - Result: Read chunks 4–6 of *Jackson v. State* (`SC2023-1298`), confirming Jackson's murders occurred in 2005 when Florida's 7–5 statute was in effect (explaining why *Hunt*, not *Jackson*, carries the federal Ex Post Facto challenge).
13. `mcp_courtlistener_read_document(opinion_id=11335438, chunk_index=0, chunk_size=4000)`
    - Result: Read chunk 0 of *Whitton v. Dixon* (`25-580`, June 1, 2026 per curiam *Napue*/*Brady* decision; unrelated to Fla. Stat. § 921.141).
14. `mcp_courtlistener_read_document(opinion_id=11228303, chunk_index=[2, 3], chunk_size=8000)`
    - Result: Read chunks 2–3 of *Jackson v. State* (`SC2023-1298`), reviewing the Florida Supreme Court's lead Sixth and Eighth Amendment analysis incorporated by reference in *Hunt*.
15. `mcp_courtlistener_search(type="o", court="scotus", q='"Poole" "Hurst" "unanimous" OR "nonunanimous" "Florida" OR "Alabama" death', fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber"])`
    - Result: `count: 0`.
16. `mcp_courtlistener_search(type="o", court="scotus", filed_after="2018-01-01", q='"10-2" OR "8-4" "unanimous" "jury" "death" Sotomayor', fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber"])`
    - Result: `count: 38` SCOTUS opinions (including *Ramos v. Louisiana*, *Edwards v. Vannoy*, and *Gutierrez v. Saenz*).

## 3. Web Searches

- None performed.
