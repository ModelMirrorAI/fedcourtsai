# Retrieval Log: `scotus/9026000292` (`evt-petition-disposition`)

- **Mode:** `forward` (`cutoff: null` in `data/cases/scotus/9026000292/record/context.json`)
- **Blinding Compliance:** No lookup of the outcome or post-snapshot disposition of `scotus/9026000292` (or its companion petitions `26-293` and `26-294`) was attempted. All queries retrieved prior docket context, companion case metadata, corpus base-rate priors, and the published pre-decision opinions below.

## 1. Local CLI & Corpus Queries (`uv run fedcourts ...`)

1. **Command:** `uv run fedcourts paths --court "scotus" --docket "9026000292" --event "evt-petition-disposition" --role predictor`
   - **Result:** Resolved `case_id` (`scotus/9026000292`), `corpus` (`corpus/corpus.db`), and `event` (`data/cases/scotus/9026000292/events/evt-petition-disposition/event.yaml`).

2. **Command:** `uv run fedcourts query --help`
   - **Result:** Displayed structured filter options for `fedcourts query`.

3. **Query:** `uv run fedcourts query --court scotus --docket-number 26-293`
   - **Transfer:** `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - **Result:** Returned 1 row for Vide companion petition *Kathleen Ashton, et al. v. The Taliban, et al.* (`scotus/9026000293`), confirming `distribution_count: 2`, `distributed_for_conference: "2026-11-13"`, `cvsg_date: null`, `response_filed_at: null`, and counsel of record Samuel Issacharoff.

4. **Query:** `uv run fedcourts query --court scotus --docket-number 26-294`
   - **Transfer:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Result:** Returned 1 row for Vide companion petition *James Owens, et al. v. The Taliban, et al.* (`scotus/9026000294`), confirming `distribution_count: 2`, `distributed_for_conference: "2026-11-13"`, `cvsg_date: null`, `response_filed_at: null`, and counsel of record Matthew Dempsey McGill.

5. **Query:** `uv run fedcourts query --court scotus --docket-number 25A1393`
   - **Transfer:** `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - **Result:** Returned 1 row for the linked extension application (`scotus/73500481`, *Fiona Havlish, et al. v. The Taliban, et al.*), granted June 18, 2026 across Second Circuit docket numbers `23-258, 23-263, 23-304, 23-346, 23-444, 23-354, 23-797`.

6. **Query:** `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - **Transfer:** `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - **Result:** Returned 10 recent OT 2026 certiorari dispositions from the November 6, 2026 Conference (decided November 9, 2026: `26-18`, `26-55`, `26-85`, `26-87`, `26-107`, `26-115`, `26-119`, `26-167`, `26-175`, `26-222`), all denied on November 9, 2026.

7. **Attempted Query (Usage Error):** `uv run fedcourts query --court scotus --originating-court ca2 --era 2020s --limit 15`
   - **Transfer:** None (exited with code 2: `No such option: --originating-court`). Re-issued immediately below using valid flags.

8. **Query:** `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - **Transfer:** `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
   - **Result:** Returned 10 recent OT 2026 grants (`25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, `25-1349`) to compare distribution counts (`distribution_count` 2 to 5 on most paid cert grants) and party/amicus participation against `26-292`.

## 2. External Lookups (CourtListener MCP)

1. **`mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `case_name="Havlish v. The Taliban"`):**
   - **Result:** `count: 0` (caption in CourtListener was indexed as `Havlish v. Taliban; Aliganga v. Taliban`).

2. **`mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `docket_number="23-258"`):**
   - **Result:** `count: 2` — located the Second Circuit panel opinion (*Havlish v. Taliban; Aliganga v. Taliban*, Cluster ID `10660852`, Opinion ID `11127439`, filed August 26, 2025, `152 F.4th 339`) and the Second Circuit order and opinions denying rehearing en banc (Cluster ID `10811059`, Opinion ID `11277807`, filed March 19, 2026, `170 F.4th 100`).

3. **`mcp_courtlistener_search` (`type="o"`, `citation="152 F.4th 339"`):**
   - **Result:** `count: 0` (F.4th reporter citation not yet attached on the CourtListener cluster record, which was already located via docket number `23-258`).

4. **`mcp_courtlistener_search` (`type="o"`, `citation="170 F.4th 100"`):**
   - **Result:** `count: 0` (already located via docket number `23-258`, Cluster ID `10811059`).

5. **`mcp_courtlistener_search` (`type="o"`, `citation="45 F.4th 1340"`):**
   - **Result:** `count: 0` (*Stansell v. Revolutionary Armed Forces of Colombia* citation lookup returned 0; analyzed from the detailed quotations in the Second Circuit panel and dissent opinions).

6. **`mcp_courtlistener_search` (`type="o"`, `citation="830 F.3d 107"`):**
   - **Result:** `count: 3` — verified the Second Circuit's prior TRIA decision in *Kirschenbaum v. 650 Fifth Avenue & Related Properties*, 830 F.3d 107 (2d Cir. 2016) (Cluster ID `4179037`).

7. **`mcp_courtlistener_read_document` (`opinion_id=11127439`, chunks `3..10` and `11..19`):**
   - **Result:** Read the complete Second Circuit panel majority opinion and Judge Sullivan's partial dissent (`156,644` chars across 20 chunks), recovering the pages (`App. 42a–78a`) truncated from `record/documents/petition.txt`.

8. **`mcp_courtlistener_read_document` (`opinion_id=11277807`, chunks `0..8` and `9..10`):**
   - **Result:** Read the complete Second Circuit en banc denial opinions (`82,791` chars across 11 chunks), recovering Judge Nardini's concurrence, Judge Sullivan's dissent (joined by Chief Judge Livingston and Judges Bianco and Park), Judge Menashi's dissent, and Judges Cabranes and Calabresi's joint statement (`App. 82a–118a`).

9. **`mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Exxon Mobil"`, `filed_after="2026-01-01"`) & `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="24-699"`):**
   - **Result:** `count: 1` — located *Exxon Mobil Corp. v. Corporación Cimex, S.A. (Cuba)*, No. 24-699, decided June 23, 2026 (Cluster ID `10878536`, Opinion ID `11346053`).

10. **`mcp_courtlistener_read_document` (`opinion_id=11346053`, chunk `0`):**
    - **Result:** Read the syllabus of *Exxon Mobil Corp. v. Corporación Cimex, S.A. (Cuba)*, holding that the Helms-Burton Act abrogates foreign sovereign immunity for Cuban agencies and instrumentalities without requiring satisfaction of an FSIA exception.

11. **`mcp_courtlistener_search` (`type="o"`, `q='"Terrorism Risk Insurance Act"'`, `filed_after="2026-08-31"`):**
    - **Result:** `count: 2` (two D.D.C. civil forfeiture opinions), confirming no federal court of appeals issued a new TRIA decision between the filing of the petition and the November 9, 2026 snapshot.
