# Retrieval Log (`scotus/9026000267` — `evt-petition-disposition`)

All lookups attempted beyond the provisioned files in `data/cases/scotus/9026000267/` are logged below, including failed or schema-rejected calls.

## 1. `fedcourts` CLI Calls

1. **`uv run fedcourts paths --court "scotus" --docket "9026000267" --event "evt-petition-disposition" --role predictor`** (alongside `uv run fedcourts query --help`)
   - **Result**: Printed resolved paths (`case_id scotus/9026000267`, `corpus corpus/corpus.db`, `event .../event.yaml`, `outcome (evaluator-only — never a predictor input)`), confirmed `DECIDED_BEFORE=` (empty; forward mode), and printed `--help` flags for `fedcourts query`.

2. **`uv run fedcourts query --court scotus --stage cert --search "502(a)(2)" --limit 25 --json`** (chained with a second `--stage`/`--search` command that did not run)
   - **Result**: Failed (`Exit Code: 2` — `No such option: --stage`; `fedcourts query` is a structured flag filter with no free-text `--search` or `--stage` option).

3. **`uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`**
   - **Stderr / read line**: `ranged corpus reads: 42 GET(s), 10944512 byte(s)`
   - **Result**: Returned 15 recent 2020s SCOTUS granted rows (including OT2026 cert grants `25-1408`, `26-12`, `26-204`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`, `26-104`, `26-426` and interim grants), confirming corpus row structure and distribution counts.

4. **`uv run fedcourts query --court scotus --docket-number 24-392`**
   - **Stderr / read line**: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - **Result**: Returned `scotus/72484103` (*Argent Trust Company v. Ramon DeJesus Cedeno, et al.*, No. 24-392): cert denied `2024-11-04`, `distribution_count: 1`, `cvsg_date: null`.

5. **`uv run fedcourts query --court scotus --docket-number 24-559`**
   - **Stderr / read line**: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - **Result**: Returned `scotus/72484866` (*Tenneco, Inc., et al. v. Tanika Parker, et al.*, No. 24-559): cert denied `2025-01-13`, `distribution_count: 1`, `cvsg_date: null`.

6. **`uv run fedcourts query --court scotus --era 2020s --include-open --limit 30`**
   - **Stderr / read line**: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Result**: Returned 30 recent OT2026 SCOTUS rows (resolved denials/GVRs from Nov. 9–12, 2026), showing `distribution_count` patterns across single-distribution and relisted petitions.

7. **`uv run fedcourts query --court scotus --era 2020s --originating-court ca9 --disposition granted --limit 15`**
   - **Result**: Failed (`Exit Code: 2` — `No such option: --originating-court`).

8. **`uv run fedcourts query --court scotus --docket-number 23-85`**
   - **Stderr / read line**: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - **Result**: Returned `scotus/72483315` (*James Giehl v. Bank of America*, No. 23-85 — wrong docket number guess for *Envision Management v. Harrison*).

9. **`uv run fedcourts query --court scotus --docket-number 23-122`**
   - **Stderr / read line**: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Result**: Returned `scotus/72479528` (*Wilmington Trust, N.A., et al. v. Marlow Henry*, No. 23-122): cert denied `2023-10-16`, `distribution_count: 1`, `cvsg_date: null`.

10. **`uv run fedcourts query --court scotus --docket-number 26-267 --include-open`**
    - **Stderr / read line**: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - **Result**: Returned the open corpus row for `scotus/9026000267` (*The Capital Group Companies, Inc., et al. v. Cathy Pover*, No. 26-267), confirming `disposition: null`, `last_live_polled: "2026-11-13"`, `distribution_count: 1`, `cvsg_date: null`, `salience_score: 0.0248`.

11. **`uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 30`**
    - **Stderr / read line**: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - **Result**: Returned 30 recent Nov. 2026 denials (including `26-107`, `26-222`, `26-18`, `25-1426`), illustrating `distribution_count >= 2` on petitions re-distributed after responses or relists.

---

## 2. CourtListener MCP Calls

1. **`mcp_courtlistener_search` (`type="o"`, `q=""Trauernicht" OR "Cedeno v. Sasson" OR "Platt v. Sodexo" OR "Williams v. Shapiro" OR "Parrott v. International Bancshares""`)**
   - **Result**: Returned 83 opinion matches, including *Cedeno v. Sasson* (`opinion_id: 9498350`, 100 F.4th 386 (2d Cir. 2024)), *Platt v. Sodexo, S.A.* (148 F.4th 709 (9th Cir. 2025)), *Trauernicht v. Genworth Financial Inc.* (`opinion_id: 11274227`, 169 F.4th 459 (4th Cir. Apr. 20, 2026)), *Williams v. Shapiro* (161 F.4th 1313 (11th Cir. 2025)), and *Parrott v. International Bancshares Corp.* (167 F.4th 728 (5th Cir. 2026)).

2. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Trauernicht" OR "Genworth" OR "Cedeno" OR "Tenneco" OR "Sodexo" OR "Shapiro" OR "International Bancshares" OR "Capital Group""`)**
   - **Result**: Returned 1,671 broad SCOTUS opinion matches (mostly unrelated criminal/civil cert denials matching common surnames like "Cedeno" or "Shapiro").

3. **`mcp_courtlistener_call_endpoint` (`endpoint_id="dockets"`, `query={"court": "scotus", "case_name__icontains": "Genworth", ...}`)**
   - **Result**: Validation error (`case_name`: extra inputs `icontains` not permitted on `DocketsEndpoint`).

4. **`mcp_courtlistener_call_endpoint` (`endpoint_id="dockets"`, `query={"court": "scotus", "case_name__icontains": "Trauernicht", ...}`)**
   - **Result**: Validation error (`case_name`: extra inputs `icontains` not permitted on `DocketsEndpoint`).

5. **`mcp_courtlistener_read_document` (`opinion_id=11274227`, `chunk_index=[0, 1, 2]`)**
   - **Result**: Returned chunks 0–2 of *Trauernicht v. Genworth Financial Inc.*, 169 F.4th 459 (4th Cir. 2026) (total 8 chunks, 63,490 chars), detailing Genworth's arbitration provision (including its explicit carveout allowing individual-account § 502(a)(2) recovery) and the procedural posture.

6. **`mcp_courtlistener_read_document` (`opinion_id=11274227`, `chunk_index=[3, 4, 5, 6]`)**
   - **Result**: Returned chunks 3–6 of *Trauernicht*, containing Judge Niemeyer's statutory and equitable reasoning under *Russell*, *LaRue*, *Thole*, and *Trump v. CASA, Inc.*, and its explicit rejection of the Second, Third, Sixth, Seventh, Ninth, and Tenth Circuits' effective-vindication holdings.

7. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Envision Management" OR "Wilmington Trust" OR "Argent Trust" OR "Tenneco" OR "Sodexo" OR "International Bancshares""`)**
   - **Result**: Returned 51 SCOTUS order/opinion matches, including *Wilmington Trust, N.A. v. Henry* (No. 23-122, cert. denied Oct. 16, 2023) and *Envision Management Holding, Inc. v. Harrison* (cert. denied Oct. 10, 2023).

---

## 3. Web Searches (`google_web_search`)

1. **Query**: `""Trauernicht" "Genworth" certiorari OR "Supreme Court" OR "26-267" "Capital Group""`
   - **Result**: Returned no search results.

2. **Query**: `""Cedeno" "Sasson" OR "Parker" "Tenneco" OR "Platt" "Sodexo" OR "Parrott" "International Bancshares" OR "Williams" "Shapiro" certiorari denied OR pending"`
   - **Result**: Returned an AI-synthesized summary of the ERISA arbitration circuit split and noted No. 26-267's pending status (noting `Response Requested` and Dec. 2, 2026 BIO due date; also inaccurately conflated whether cert was denied vs. never sought in *Platt*/*Parrott*/*Williams*, which I cross-checked against Petitioners' Table of Authorities in `petition.txt`). Grounding links included `scotusgate.com` (never opened; disclosed in `flags.json`).

3. **Query**: `""Trauernicht v. Genworth" rehearing OR "en banc" OR certiorari OR "Supreme Court""`
   - **Result**: Confirmed Fourth Circuit panel decision on Apr. 20, 2026, rehearing en banc denied Sept. 16, 2026, and no separate cert petition filed in *Trauernicht* as of mid-November 2026 (90-day cert window open until Dec. 15, 2026). Grounding links included `scotusgate.com` (never opened; disclosed in `flags.json`).

4. **Query**: `""Parrott" "International Bancshares" "Supreme Court" OR "25-" OR "26-" certiorari"`
   - **Result**: Confirmed *Parrott v. International Bancshares Corp.*, 167 F.4th 728 (5th Cir. 2026), had no SCOTUS cert petition filed; AI search summary also characterized No. 26-267 in generic prose as "the most active and likely candidate for a grant of certiorari" (disregarded and disclosed in `flags.json`).

5. **Query**: `""Trauernicht" "supremecourt.gov" OR "Petition for a writ of certiorari" "Genworth""`
   - **Result**: Confirmed *Trauernicht* is cited heavily in No. 26-267 (*Capital Group v. Pover*) with no separate *Trauernicht* cert petition docketed on supremecourt.gov yet; AI search overview generically described No. 26-267 as the vehicle "expected to address" the issue (disregarded and disclosed in `flags.json`).

6. **Query**: `""International Bancshares" "Parrott" "supremecourt.gov" OR "Shapiro" "Williams" "161 F.4th" "supremecourt.gov" OR "Sodexo" "Platt" "supremecourt.gov""`
   - **Result**: Confirmed those three circuit decisions were cited in No. 26-267's petition rather than having separate cert dockets on supremecourt.gov.

7. **Query**: `""Trauernicht" "24-1880" "en banc" OR "mandate" OR "certiorari" 2026"`
   - **Result**: Confirmed Fourth Circuit docket No. 24-1880 rehearing en banc denial on Sept. 16, 2026. Grounding links included `scotusgate.com` (never opened; disclosed in `flags.json`).

8. **Query**: `""26-267" "Capital Group" "amici" OR "ERIC" OR "Mayer Brown" OR "Chamber" 2026"`
   - **Result**: Summarized the Nov. 2, 2026 amicus brief filed by Mayer Brown LLP (Andrew J. Pincus) on behalf of The American Benefits Council, CIEBA, and The ERISA Industry Committee supporting Petitioners.

9. **Query**: `""Sodexo" "Platt" "Docket No." OR "25-" site:supremecourt.gov"`
   - **Result**: Tool error (`TypeError: fetch failed sending request`).

10. **Query**: `""International Bancshares" "Parrott" OR "Shapiro" "Williams" site:supremecourt.gov"`
    - **Result**: Returned supremecourt.gov PDF match to No. 26-267 (*Capital Group v. Pover* petition), confirming neither *Parrott* nor *Williams* generated a separate SCOTUS cert docket.
