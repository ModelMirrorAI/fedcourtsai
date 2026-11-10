# Retrieval Log

## 1. Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000117" --event "evt-order-relist-disposition" --role predictor`
   - Output: resolved `case_id scotus/9026000117`, `corpus corpus/corpus.db`, `event data/cases/scotus/9026000117/events/evt-order-relist-disposition/event.yaml`.
2. `uv run fedcourts query --help`
   - Output: CLI help text for structured corpus filters.
3. `uv run fedcourts query --court scotus --docket-number 25-274`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/73275213` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*, No. 25-274, `date_cert_granted: "2026-05-11"`, `disposition: "gvr"`, `distribution_count: 2`).
4. `uv run fedcourts query --court scotus --docket-number 26-118`
   - `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
   - Returned `scotus/9026000118` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*, No. 26-118, pending companion § 1253 appeal, `distribution_count: 3`, `distributed_for_conference: "2026-11-13"`).
5. `uv run fedcourts query --court scotus --docket-number 26-119`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9026000119` (*Guam v. Richard Y. Ybanez, et al.*, No. 26-119, unrelated cert petition denied 2026-11-09).
6. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned 10 recent OT2026 granted SCOTUS cases.
7. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
   - Returned 10 recent OT2026 GVR SCOTUS cases, including *Benancio Garcia, III v. Steven Hobbs*, No. 25-901 (`scotus/73280412`) and *Jose A. Trevino v. Steven Hobbs*, No. 25-918 (`scotus/73280426`).
8. `uv run fedcourts query --court scotus --docket-number 26-116`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9026000116` (*Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.*, No. 26-116, pending companion petition for certiorari before judgment, `distribution_count: 3`, `distributed_for_conference: "2026-11-13"`).
9. `uv run fedcourts query --court scotus --docket-number 24-109`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/69779623` (*Louisiana v. Phillip Callais, et al.*, No. 24-109, `disposition: "granted"`, `merits_decided: "2026-04-29"`, `merits_judgment: "affirmed"`).
10. `uv run fedcourts query --court scotus --disposition summary-reversed --limit 10`
    - Failed with usage error (`Unknown disposition 'summary-reversed'; choose one of: granted, denied, granted-in-part, gvr, summary-reversal, dismissed, withdrawn, other`).
11. `uv run fedcourts query --court scotus --disposition dismissed --limit 10`
    - `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned 10 recent dismissed SCOTUS cases.
12. `uv run fedcourts query --court scotus --docket-number 25-273`
    - `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned `scotus/73275215` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*, No. 25-273, `date_cert_granted: "2026-05-11"`, `disposition: "gvr"`, `distribution_count: 2`).
13. `uv run fedcourts query --court scotus --disposition summary-reversal --limit 10`
    - `ranged corpus reads: 1093 GET(s), 286523392 byte(s)`
    - Returned 0 rows.
14. `uv run fedcourts query --court scotus --disposition other --limit 10`
    - `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
    - Returned 10 historical `other`-disposition SCOTUS rows.
15. `uv run fedcourts query --court scotus --docket-number 25-272`
    - `ranged corpus reads: 16 GET(s), 4194304 byte(s)`
    - Returned `scotus/73275212` (*Andy Luu Tran v. Herbert Jacobs*, No. 25-272, unrelated).
16. `uv run fedcourts query --court scotus --docket-number 25-275`
    - `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned `scotus/73275214` (*Clifford James Frost, Jr. v. Dana Nessel*, No. 25-275, unrelated).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Allen v. Milligan", filed_after="2026-01-01")`
   - Returned 1 match: *Allen v. Milligan*, No. 25A1314 (`cluster_id=10869022`, `opinion_id=11336479`, filed 2026-06-02).
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="Abbott v. LULAC", filed_after="2025-01-01")`
   - Returned 0 matches.
3. `mcp_courtlistener_read_document(opinion_id=11336479)` (full read and chunk read `chunk_index=[0, 1, 2]`)
   - Retrieved the Supreme Court's June 2, 2026 Per Curiam stay opinion, Justice Kavanaugh's concurrence, and Justice Sotomayor's dissent in *Allen v. Milligan*, 608 U.S. ___, 146 S. Ct. 1377 (2026).
4. `mcp_courtlistener_search(type="o", court="scotus", q="Abbott LULAC", filed_after="2026-04-20", filed_before="2026-05-05")`
   - Returned 0 matches.
5. `mcp_courtlistener_search(type="o", court="scotus", case_name="Louisiana v. Callais", filed_after="2026-04-01")`
   - Returned 2 matches: *Louisiana v. Callais*, No. 24-109 (`cluster_id=10851396`, `opinion_id=11320154`, filed 2026-04-29; and revisions `cluster_id=10852760`, filed 2026-05-04).
6. `mcp_courtlistener_search(type="o", court="scotus", case_name="Allen v. Caster", filed_after="2026-01-01")`
   - Returned 0 matches.
7. `mcp_courtlistener_search(type="o", court="scotus", case_name="Abbott v. League of United Latin American Citizens", filed_after="2025-01-01")`
   - Returned 0 matches.
8. `mcp_courtlistener_search(type="r", court="alnd", docket_number="2:21-cv-01530")`
   - Returned RECAP docket `docket_id=61494291` (*Milligan v. Allen*, N.D. Ala.).
9. `mcp_courtlistener_search(type="r", court="alnd", docket_number="2:21-cv-01291")`
   - Returned RECAP docket `docket_id=60607496` (*Singleton v. Allen*, N.D. Ala.).
10. `mcp_courtlistener_search(type="rd", court="alnd", docket_number="2:21-cv-01530", entry_date_filed_after="2026-05-25", order_by="entry_date_filed desc")`
    - Returned 10 post-May 25, 2026 docket entries in *Milligan v. Allen* (Docs. 537–546).
11. `mcp_courtlistener_read_document(recap_document_id=492999516)`
    - Retrieved *Milligan* Doc. 544 (Order on Outstanding Motions, filed July 20, 2026).
12. `mcp_courtlistener_read_document(recap_document_id=480335147, chunk_index=19)` and `chunk_index=[16, 17]`
    - Retrieved *Milligan* Doc. 537 (Preliminary Injunction Order, filed May 26, 2026, pages 73–92 of 102, including the operative preliminary injunction and scheduling order on pages 76–79).
13. `mcp_courtlistener_search(type="o", court="scotus", q=""judgment is vacated" "remanded to the United States District Court" "dismiss" "moot"")`
    - Returned 8 historical Supreme Court *Munsingwear* vacatur orders on direct appeals and cert petitions.
14. `mcp_courtlistener_search(type="o", court="scotus", q=""Munsingwear" "United States District Court"", filed_after="2020-01-01")`
    - Returned 2 matches (*Acheson Hotels, LLC v. Laufer*, 601 U.S. 1 (2023)).
