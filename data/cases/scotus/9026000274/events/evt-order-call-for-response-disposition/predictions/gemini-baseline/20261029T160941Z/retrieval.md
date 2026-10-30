# Retrieval Log (`scotus/9026000274` — `evt-order-call-for-response-disposition`)

## 1. Corpus Queries (`uv run fedcourts query`)

1. **Command:** `uv run fedcourts query --help`
   - **Transfer:** none (help output)
   - **Result:** Inspected structured filter options (`--court`, `--docket-number`, `--topic`, `--judge`, `--citation`, `--disposition`, `--era`, `--decided-before`).

2. **Command:** `uv run fedcourts query --court scotus --docket-number 26-274 --limit 5`
   - **Transfer:** `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - **Result:** Returned 1 row (`scotus/9026000274`, *Francisco Xavier Ortiz-Colón v. United States*, docket `26-274`, originating court `ca1` docket `23-1504`, `salience_score: 0.0145`, `salience_version: "sal-v4"`).

3. **Command:** `uv run fedcourts query --court scotus --citation "146 S.Ct. 482" --citation "143 S.Ct. 121" --limit 10`
   - **Transfer:** `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - **Result:** 0 rows returned (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

4. **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - **Transfer:** `ranged corpus reads: 28 GET(s), 7143424 byte(s)`
   - **Result:** Returned 10 recent granted SCOTUS priors in the 2020s era (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`).

5. **Command:** `uv run fedcourts query --court ca1 --judge Barron --judge Thompson --judge Gelpí --limit 10`
   - **Transfer:** `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
   - **Result:** 0 rows returned (circuit judge lists are withheld in the corpus slice).

## 2. CourtListener MCP Calls

1. **Tool:** `mcp_courtlistener_search`
   - **Arguments:** `{"court": "ca1", "docket_number": "23-1504", "fields": ["caseName", "citation", "dateFiled", "cluster_id", "opinions"], "type": "o"}`
   - **Result:** Error (`Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 9262 seconds.'}`). Degraded gracefully per prompt instructions without retrying CourtListener.

## 3. Forward-Mode Web Searches (`google_web_search`)

1. **Query:** `"United States v. Ortiz-Colón" "23-1504" "Blockburger" OR "2251(a)" "2422(b)"`
   - **Result:** Confirmed the First Circuit's May 6, 2026 holdings in *United States v. Ortiz-Colón*, No. 23-1504 (1st Cir. 2026): (1) vacating one of the receipt/possession counts under 18 U.S.C. § 2252A(a)(2) and (a)(5)(B) on plain-error review as lesser-included offenses, and (2) affirming the simultaneous convictions under 18 U.S.C. § 2251(a) and 18 U.S.C. § 2422(b) under *Blockburger* because § 2251(a) requires actual production of child pornography while § 2422(b) requires coercion or enticement of a minor to engage in chargeable sexual activity. Also confirmed that No. 26-274 remains pending on certiorari.

2. **Query:** `"Barrett v. United States" "146 S. Ct. 482" OR "607 U.S. 128" "Blockburger"`
   - **Result:** No results returned for the exact quoted string.

3. **Query:** `"Barrett v. United States" 2026 "Blockburger" "924"`
   - **Result:** Retrieved summary of *Barrett v. United States*, 607 U.S. 128 (decided Jan. 14, 2026; opinion by Justice Jackson, concurrence by Justice Gorsuch), holding that a single act violating both 18 U.S.C. § 924(c) and § 924(j) may yield only one conviction under the *Blockburger* presumption because § 924(c) is a lesser-included offense of § 924(j) and Congress did not clearly authorize cumulative punishments.
