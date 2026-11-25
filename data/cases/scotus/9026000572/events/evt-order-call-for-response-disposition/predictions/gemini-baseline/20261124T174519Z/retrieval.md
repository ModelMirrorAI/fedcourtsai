# Retrieval Log

Mode in `record/context.json`: `forward` (`snapshot_date: "2026-11-24"`, `cutoff: "2026-11-25"`). No outcome or external forecast of this case was sought or encountered.

## 1. Local `fedcourts` CLI and Corpus Queries

1. **Path resolution and query CLI inspection (local metadata only, no corpus reads):**
   - Command: `uv run fedcourts paths --court "scotus" --docket "9026000572" --event "evt-order-call-for-response-disposition" --role predictor && uv run fedcourts query --help`
   - Result: Confirmed predictor input paths and `fedcourts query` flags; `$DECIDED_BEFORE` unset (`forward` mode).

2. **Corpus citation lookup for Supreme Court INA §§ 1225/1226 detention precedents:**
   - Command: `uv run fedcourts query --court scotus --citation "583 U.S. 281" --citation "586 U.S. 392" --citation "591 U.S. 103" --citation "596 U.S. 573" --limit 10`
   - Corpus read stats: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned, with coverage note (`only 195 row(s) in scope (scotus) carry any reporter citation at all`).

3. **Corpus lookup for recent 2020s SCOTUS GVR dispositions (checking `distribution_count` patterns on held/GVR'd petitions):**
   - Command: `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - Corpus read stats: `ranged corpus reads: 39 GET(s), 10092544 byte(s)`
   - Result: 10 resolved GVR rows returned (`scotus/73538544` No. 25-1421, `scotus/9026005528` No. 26-5528, `scotus/73278467` No. 25-442, `scotus/73500249` No. 25-1348, `scotus/9026005123` No. 26-5123, `scotus/73317900` No. 25-1269, `scotus/73500268` No. 25-1367, `scotus/73500579` No. 25-7569, `scotus/9026000139` No. 26-139, `scotus/9026005216` No. 26-5216), showing `distribution_count >= 2` across paid non-IFP GVRs.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="175 F.4th 61", num_results=5, fields=["caseName","citation","court_id","dateFiled","docketNumber","judge","cluster_id"])` -> `query_id: a979b8cf`, `count: 0` (recent F.4th cite not yet indexed in citation field).
2. `mcp_courtlistener_search(type="o", citation="166 F.4th 494", num_results=5, fields=["caseName","citation","court_id","dateFiled","docketNumber","judge","cluster_id"])` -> `query_id: 7444b150`, `count: 0`.
3. `mcp_courtlistener_search(type="d", court="scotus", case_name="Barbosa da Cunha", num_results=5, fields=["caseName","docketNumber","dateFiled","docket_id"])` -> `query_id: 94c519c8`, `count: 0`.
4. `mcp_courtlistener_search(type="o", case_name="Barbosa da Cunha", num_results=5, fields=["caseName","citation","court_id","dateFiled","docketNumber","judge","cluster_id"])` -> `query_id: 6830aec7`, `count: 1`: *Barbosa Da Cunha v. Freden*, No. 25-3141 (2d Cir., cluster `10983473`).
5. `mcp_courtlistener_search(type="o", case_name="Buenrostro-Mendez", num_results=5, fields=["caseName","citation","court_id","dateFiled","docketNumber","judge","cluster_id"])` -> `query_id: a514b5c5`, `count: 0`.

## 3. Web Search (Lead Case Status Only)

1. `google_web_search(query='site:supremecourt.gov "26-104" "Barbosa da Cunha"')`
   - Result: Confirmed status of the granted lead case *Rhoney v. Barbosa da Cunha*, No. 26-104 (cert. granted October 1, 2026 on whether 8 U.S.C. § 1225(b)(2)(A) mandates detention pending removal proceedings of noncitizens present in the United States without having been admitted; oral argument expected in early 2027, with related pending petitions including No. 25-1415 and No. 26-43; circuit split spanning the 2d, 3d, 6th, 7th, and 11th Circuits against the 5th and 8th Circuits). No third-party forecasts or odds surfaced.
