# Retrieval Log

## 1. Corpus CLI Lookups (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000116" --event "evt-order-relist-disposition" --role predictor` and `uv run fedcourts query --help`
   - No transfer line (path resolution and CLI help).
2. `uv run fedcourts query --court scotus --docket-number 26-117`
   - `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned `scotus/9026000117` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*, No. 26-117, pending companion appeal, `distributed_for_conference: "2026-11-13"`, `distribution_count: 3`).
3. `uv run fedcourts query --court scotus --docket-number 26-118`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9026000118` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*, No. 26-118, pending companion appeal, `distributed_for_conference: "2026-11-13"`, `distribution_count: 3`).
4. `uv run fedcourts query --court scotus --docket-number 25-243`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/73275185` (*Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.*, No. 25-243, prior petition for certiorari before judgment, `disposition: "granted"`, `date_cert_granted: "2026-05-11"`, `merits_decided: "2026-05-11"`, `merits_judgment: "vacated"`, `distribution_count: 2`).
5. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1131"`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (note on sparse `citations` column).
6. `uv run fedcourts query --court scotus --citation "608 U.S. 511"`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 0 rows (note on sparse `citations` column).
7. `uv run fedcourts query --court scotus --disposition gvr --limit 10`
   - `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
   - Returned 10 recent GVR rows in `scotus`, including VRA redistricting GVRs `25-901` (*Garcia v. Hobbs*, decided 2026-10-05, `distribution_count: 3`) and `25-918` (*Trevino v. Hobbs*, decided 2026-10-05, `distribution_count: 2`), as well as `26-5123`, `25-1269`, `25-1367`, `25-7569`, `26-139`, `26-5216`, `25-7462`, and `25-7532`.
8. `uv run fedcourts query --court scotus --docket-number 25A1316`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/73500400` (*Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.*, No. 25A1316, emergency stay application granted `2026-06-02`).
9. `uv run fedcourts query --court scotus --disposition granted --limit 10`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent granted rows in `scotus` (`25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`).
10. `uv run fedcourts query --court scotus --era 2020s --disposition vacated --limit 10`
    - Failed with usage error (exit code 2): `Unknown disposition 'vacated'; choose one of: granted, denied, granted-in-part, gvr, summary-reversal, dismissed, withdrawn, other`.
11. `uv run fedcourts query --court scotus --disposition summary-reversal --limit 10`
    - `ranged corpus reads: 1029 GET(s), 269746176 byte(s)`
    - Returned 0 rows.
12. `uv run fedcourts query --court scotus --disposition other --limit 10`
    - `ranged corpus reads: 370 GET(s), 96993280 byte(s)`
    - Returned 10 historical rows with `disposition: "other"`.
13. `uv run fedcourts query --court scotus --docket-number 25-241`, `25-242`, `25-244`
    - `ranged corpus reads: 14 GET(s), 3670016 byte(s)` (for `25-241`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-242`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-244`)
    - Returned unrelated OT2025 dockets (`25-241`, `25-242`, `25-244`).
14. `uv run fedcourts query --court scotus --docket-number 25-245`, `25-246`
    - `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-245`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-246`)
    - Returned unrelated OT2025 dockets (`25-245`, `25-246`).
15. `uv run fedcourts query --court scotus --docket-number 25-248`, `25-249`, `25A1314`, `25A1315`
    - `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25-248`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-249`), `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25A1314`), `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25A1315`)
    - Returned `25-248` (*District of Columbia v. R.W.*), `25-249` (*Poon-Atkins*), `25A1314` (*Allen v. Milligan* stay application granted `2026-06-02`), and `25A1315` (*Allen v. Singleton* stay application granted `2026-06-02`).
16. `uv run fedcourts query --court scotus --docket-number 25-987`, `25-256`, `25-257`
    - `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25-987`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-256`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-257`)
    - Returned unrelated OT2025 dockets (`25-987`, `25-256`, `25-257`).
17. `uv run fedcourts query --court scotus --docket-number 25-897`, `25-240`, `25-247`
    - `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25-897`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-240`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-247`)
    - Returned unrelated OT2025 dockets (`25-897`, `25-240`, `25-247`).
18. `uv run fedcourts query --court scotus --docket-number 25-293`, `25-295`, `25-887`
    - `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25-293`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-295`), `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25-887`)
    - Returned unrelated OT2025 dockets (`25-293`, `25-295`, `25-887`).
19. `uv run fedcourts query --court scotus --docket-number 25-298`, `25-299`, `25-807`
    - `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-298`), `ranged corpus reads: 0 GET(s), 0 byte(s)` (for `25-299`), `ranged corpus reads: 1 GET(s), 262144 byte(s)` (for `25-807`)
    - Returned unrelated OT2025 dockets (`25-298`, `25-299`, `25-807`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Abbott v. League of United Latin American Citizens", filed_before="2026-11-10", fields=["caseName", "dateFiled", "citation", "cluster_id", "opinions"])`
   - Returned `count: 0`.
2. `mcp_courtlistener_search(type="o", court="scotus", q='"Abbott" AND ("League of United Latin" OR "LULAC")', filed_after="2025-01-01", filed_before="2026-11-10", fields=["caseName", "dateFiled", "citation", "cluster_id", "opinions"])`
   - Returned `count: 5`, including *Louisiana v. Callais* (cluster `10852760` / `10847527`) and *Allen v. Milligan* stay opinion (cluster `10869022`).
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Louisiana v. Callais", filed_after="2025-01-01", filed_before="2026-11-10", fields=["caseName", "dateFiled", "citation", "cluster_id", "opinions"])`
   - Returned `count: 2` (*Louisiana v. Callais*, `opinion_id: 11320154` / `11314893`, decided `2026-04-29`).
4. `mcp_courtlistener_read_document(opinion_id=11320154, chunk_index=0)`
   - Read chunk 0 of *Louisiana v. Callais* syllabus and opening text.
5. `mcp_courtlistener_read_document(opinion_id=11320154, chunk_index=1)`
   - Read chunk 1 of *Louisiana v. Callais* syllabus.

## 3. Web Searches

- None attempted.
