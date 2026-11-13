# Retrieval Log

## Corpus CLI (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000561" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Confirmed cell paths (`case_id: scotus/9026000561`, `event: data/cases/scotus/9026000561/events/evt-petition-disposition/event.yaml`, `DECIDED_BEFORE` unset / forward mode) and inspected CLI flags.
   - No corpus transfer line (local path/help invocation).

2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 9 GET(s), 2293760 byte(s)`
   - Returned 10 recent 2020s SCOTUS cert/application denials for baseline comparison of distribution counts, counsel, and salience scores.

3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Returned 10 recent 2020s SCOTUS grants (showing SG petitioners, multi-amicus support, and multiple distributions on granted paid petitions).

4. `uv run fedcourts query --court scotus --originating-court cadc --decided-before 2026-10-28 --limit 15`
   - Attempted filter on originating court; CLI exited with code 2 (`No such option: --originating-court`) and printed valid flag documentation. No transfer line.

5. `uv run fedcourts query --court scotus --party "Drug Enforcement Administration" --decided-before 2026-10-28 --limit 15`
   - Attempted filter on party; CLI exited with code 2 (`No such option: --party`) and printed valid flag documentation. No transfer line.

6. `uv run fedcourts query --court cadc --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Returned 10 recent 2020s D.C. Circuit rows in the corpus.

7. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from warm local corpus service cache)
   - Returned 10 recent 2020s SCOTUS GVR dispositions for comparison against summary-disposition pathways.

## CourtListener MCP (`courtlistener`)

1. `search(type="o", q=""824(c)(3)" "corrective action plan"", num_results=10, fields=["caseName","court","dateFiled","citation","cluster_id","opinions","snippet"])`
   - Result: HTTP 429 rate-limit error (`Rate limit exceeded: 25/min. Expected available in 1 second.`).

2. `search(type="o", q=""824(c)(3)" "corrective action plan"", num_results=10, fields=["caseName","court","dateFiled","citation","cluster_id","opinions","snippet"])` (retry)
   - Result: `count: 0`, `results: []` (confirming no published judicial opinions match both exact quoted strings together, since opinions cite `§ 824(c)` or `§ 824(c)(2)(A)–(C)` rather than the exact string `"824(c)(3)"`).

3. `search(type="o", q=""corrective action plan" "Drug Enforcement Administration"", num_results=10, fields=["caseName","court","dateFiled","citation","cluster_id","opinions","snippet"])`
   - Result: HTTP 429 rate-limit error (`Expected available in 1 second.`).

4. `search(type="o", case_name="Ashraf", q=""824"", num_results=10, fields=["caseName","court","dateFiled","citation","cluster_id","opinions","snippet"])`
   - Result: HTTP 429 rate-limit error (`Expected available in 1 second.`).

5. `search(type="o", case_name="Ashraf", q=""corrective action plan"", num_results=5, fields=["caseName","court","dateFiled","citation","cluster_id","opinions","snippet"])`
   - Result: `count: 1` — *Sualeh Ashraf v. United States Drug Enforcement Administration*, No. 23-10340 (11th Cir. Sept. 3, 2025) (`cluster_id: 10665536`, `opinion_id: 11132123`).

6. `read_document(opinion_id=11132123)`
   - Result: Full text (`43,448` chars) of *Ashraf v. DEA* (11th Cir. Sept. 3, 2025), including Judge Abudu's majority opinion describing 21 U.S.C. § 824(c) and the Administrator's rejection of Dr. Ashraf's CAP, and Judge Tjoflat's concurrence explaining that a CAP is not a substitute for requesting an ALJ hearing or filing a written statement contesting factual allegations.

7. `search(type="o", q=""corrective action plan" "824"", num_results=10, fields=["caseName","court","dateFiled","citation","cluster_id","docketNumber"])`
   - Result: HTTP 429 rate-limit error (`Expected available in 3 seconds.`).

8. `search(type="o", q=""corrective action plan" "824"", num_results=10, fields=["caseName","court","dateFiled","citation","cluster_id","docketNumber"])` (retry)
   - Result: `count: 71` (mostly unrelated cases matching page/citation number `824`); the only federal DEA registration cases in the top results were *Sualeh Ashraf v. DEA* (11th Cir. 2025) and *Prescript Pharmaceuticals, Inc. v. U.S. Department of Justice*, No. 2024-2729 (D.D.C. May 16, 2025) (`cluster_id: 10585814`), confirming the absence of any circuit split on 21 U.S.C. § 824(c)(3).

9. `get_endpoint_item(endpoint_id="clusters", item_id=10585814, fields=["id","case_name","date_filed","sub_opinions"])`
   - Result: Returned sub-opinion `11052402` for *Prescript Pharmaceuticals, Inc. v. U.S. Department of Justice* (D.D.C. May 16, 2025).

10. `search_document(opinion_id=11052402, query="corrective action", snippet_size=500)`
    - Result: `match_count: 0` (line break split `"corrective

action"` in raw opinion HTML).

11. `search_document(opinion_id=11052402, query="824", snippet_size=500)`
    - Result: `match_count: 6` — confirmed *Prescript Pharmaceuticals* concerned immediate suspension orders under 21 U.S.C. § 824(d) and cited § 824(c)(2)(A)–(C) only as background contrast.

12. `search(type="d", court="scotus", case_name="Ashraf", num_results=5, fields=["caseName","docketNumber","dateFiled","dateTerminated"])`
    - Result: `count: 0`, `results: []` (no SCOTUS cert docket found for *Ashraf*).

## Web Search

- None attempted (`google_web_search` and `web_fetch` not called).
