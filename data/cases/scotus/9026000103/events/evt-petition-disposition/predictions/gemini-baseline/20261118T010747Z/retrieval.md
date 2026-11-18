# Retrieval Log (`scotus/9026000103` / `evt-petition-disposition` / `20261118T010747Z`)

Mode: `forward` (`DECIDED_BEFORE` unset / `null`). Zero web searches (`google_web_search` / `web_fetch`) were attempted. Never queried for the disposition or forecasts of No. 26-103.

## 1. CLI Path & Corpus Lookups (`uv run fedcourts ...`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000103" --event "evt-petition-disposition" --role predictor`
   - Returned `case_id: scotus/9026000103`, `corpus: corpus/corpus.db`, `event: data/cases/scotus/9026000103/events/evt-petition-disposition/event.yaml`, `outcome: (evaluator-only — never a predictor input)`. (No transfer line.)
2. `uv run fedcourts query --help`
   - Inspected CLI filter options. (No transfer line.)
3. `uv run fedcourts query --court scotus --citation "580 U.S. 1182" --limit 5`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows, plus CLI note explaining that `citations` holds a case's own parallel cites on 195 SCOTUS rows rather than a citing-authority graph.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Returned 10 recent OT2026 denied SCOTUS priors (e.g., `scotus/9526000698`, `scotus/73272491`, `scotus/73286452`, `scotus/9026000062`) showing typical distribution counts, counsel, and salience scores.
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer line: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Returned 5 recent OT2026 granted SCOTUS priors (`scotus/73280982`, `scotus/9026000239`, `scotus/9526000560`, `scotus/73520108`, `scotus/9526000512`).
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --judge "Thomas" --limit 10`
   - Transfer line: `ranged corpus reads: 743 GET(s), 194772992 byte(s)`
   - Returned 0 rows (cert-denial rows in the corpus carry `judges: []`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", q='"Foreign Commerce Clause"', fields=["caseName", "dateFiled", "citation", "judge", "cluster_id", "snippet"], num_results=10)`
   - Returned 24 total matches (10 shown), including `Learning Resources, Inc. v. Trump` (No. 24-1287, decided 2026-02-20), `Abitron Austria GmbH v. Hetronic Int'l, Inc.` (600 U.S. 412, 2023), `Haaland v. Brackeen` (599 U.S. 255, 2023), and older Foreign Commerce Clause opinions.
2. `mcp_courtlistener_search(type="o", q='"Foreign Commerce Clause" AND ("Baston" OR "Davila-Mendoza" OR "Rife")', filed_after="2020-01-01", fields=["caseName", "court_id", "dateFiled", "citation", "snippet"], num_results=15)`
   - Returned 8 circuit decisions from 2020–2025 discussing the Foreign Commerce Clause and *Baston*/*Davila-Mendoza*/*Rife*, including `United States v. Rife` (6th Cir. 2022), `United States v. Davila-Mendoza` (11th Cir. 2020), `United States v. Corrigan Clay` (3d Cir. 2025-02-03), and `United States v. Jordan Jysae Pulido` (11th Cir. 2025-04-08).
3. `mcp_courtlistener_search(type="o", court="scotus", q='"Foreign Commerce Clause" OR "Baston v. United States"', filed_after="2016-01-01", order_by="dateFiled desc", fields=["caseName", "dateFiled", "citation", "docketNumber", "judge", "cluster_id"], num_results=15)`
   - Returned 6 clusters (`Learning Resources, Inc. v. Trump`, `Abitron Austria GmbH`, `Haaland v. Brackeen`). Confirmed no recent post-2023 Supreme Court separate writings citing *Baston* on the Foreign Commerce Clause.
4. `mcp_courtlistener_search(type="o", q='"128 F.4th 163" OR "133 F.4th 1256" OR "Corrigan Clay v. United States" OR "Pulido v. United States" OR "Rife v. United States" OR "Park v. United States"', fields=["caseName", "court_id", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"], num_results=10)`
   - Returned 284 broad matches (name-overlap hits on `Pulido v. United States`, `Park v. United States`, etc.).
5. `mcp_courtlistener_search(type="d", court="cadc", docket_number="24-5218", fields=["caseName", "docketNumber", "dateFiled", "docket_id"], num_results=5)`
   - Returned 1 result: D.C. Circuit docket `69214448` (`United States v. All Petroleum-Product Cargo Onboard the M/T Arina`, No. 24-5218).
6. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10799354, fields=["id", "case_name", "date_filed", "sub_opinions", "judges", "syllabus"])`
   - Returned cluster metadata for `Learning Resources, Inc. v. Trump` (`opinion_id: 11266028`).
7. `mcp_courtlistener_search(type="o", citation="128 F.4th 163", fields=["caseName", "dateFiled", "cluster_id", "opinions"])`
   - Returned `United States v. Corrigan Clay`, 128 F.4th 163 (3d Cir. 2025-02-03), `opinion_id: 10792715`.
8. `mcp_courtlistener_search(type="o", citation="133 F.4th 1256", fields=["caseName", "dateFiled", "cluster_id", "opinions"])`
   - Returned `United States v. Jordan Jysae Pulido`, 133 F.4th 1256 (11th Cir. 2025-04-08), `opinion_id: 10840996`.
9. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69214448, "fields": ["id", "date_filed", "entry_number", "description"]}, num_results=30)`
   - Failed with HTTP 429 (`Rate limit exceeded: 25/min. Expected available in 2 seconds`).
10. `mcp_courtlistener_search_document(opinion_id=[11266028, 10792715, 10840996], query="Foreign Commerce Clause", snippet_size=450)`
    - First attempt returned HTTP 429 (`Expected available in 3 seconds`) on all 3 opinion IDs.
11. `mcp_courtlistener_search_document(opinion_id=[11266028, 10792715, 10840996], query="Foreign Commerce Clause", snippet_size=450)` (retry after cooldown)
    - Succeeded: `Learning Resources` (`11266028`) had 1 tangential mention; `Corrigan Clay` (`10792715`) had 63 matches (Third Circuit majority and Porter concurrence debating originalist Foreign Commerce Clause scope in non-commercial § 2423(c) context); `Pulido` (`10840996`) had 7 matches (Eleventh Circuit applying *Davila-Mendoza* framework).
12. `mcp_courtlistener_search(type="o", court="scotus", case_name="Clay v. United States", filed_after="2025-01-01", fields=["caseName", "dateFiled", "citation", "docketNumber", "opinions"], num_results=10)`
    - Failed with HTTP 429 (`Expected available in 31 seconds`).
13. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 69214448, "fields": ["id", "date_filed", "entry_number", "description"]}, num_results=30)`
    - Failed with HTTP 429 (`Expected available in 31 seconds`). Not retried further because Appendix A and Appendix B already provided the complete lower-court procedural history.
14. `mcp_courtlistener_search(type="o", court="scotus", q='"Corrigan Clay" OR "128 F.4th 163" OR "133 F.4th 1256"', filed_after="2025-01-01", fields=["caseName", "dateFiled", "citation", "docketNumber", "judge", "opinions"], num_results=10)`
    - Returned 0 results (neither *Corrigan Clay* nor *Pulido* produced a Supreme Court opinion or separate writing).
15. `mcp_courtlistener_search(type="o", citation="580 U.S. 1182", fields=["caseName", "dateFiled", "cluster_id", "opinions"])`
    - Returned 0 results.
16. `mcp_courtlistener_search(type="d", court="scotus", case_name="Clay v. United States", filed_after="2025-01-01", fields=["caseName", "docketNumber", "dateFiled", "docket_id"], num_results=5)`
    - Returned 0 results.
17. `mcp_courtlistener_search(type="o", court="scotus", case_name="Baston v. United States", fields=["caseName", "dateFiled", "citation", "cluster_id", "opinions"])`
    - Returned 0 results (key excerpts from Justice Thomas's *Baston* dissent are already quoted verbatim in `petition.txt` and `questions-presented.txt`).
