# Retrieval Log: `scotus/9026000424` / `evt-petition-disposition` (`20261116T143731Z`)

## 1. Mode and Leakage Boundaries

- **Mode:** `forward` (`record/context.json`: `"mode": "forward"`, `"decided_before": null`, `"cutoff": null`, `"snapshot_date": "2026-11-16"`).
- **Environment check:** `DECIDED_BEFORE` was verified empty/unset in the shell (`DECIDED_BEFORE=`), matching forward-mode live prediction on an open OT2026 petition distributed on November 10, 2026 for the December 4, 2026 Conference.
- **Blinding & Forecast Hygiene:** No `outcome.yaml`, `evaluations/**`, other predictors' `predictions/**` directories, git history for outcomes, or third-party external forecasts/commentary on No. 26-424 were accessed.

## 2. Provisioned Workspace Inputs Read

- `data/cases/scotus/9026000424/events/evt-petition-disposition/event.yaml`
- `data/cases/scotus/9026000424/record/context.json`
- `data/cases/scotus/9026000424/record/snapshots/2026-11-16.json`
- `data/cases/scotus/9026000424/record/documents/documents.json`
- `data/cases/scotus/9026000424/record/documents/questions-presented.txt`
- `data/cases/scotus/9026000424/record/documents/lower-court-docket.txt`
- `data/cases/scotus/9026000424/record/documents/decision-below.txt`
- `data/cases/scotus/9026000424/record/documents/appendix.txt`
- `data/cases/scotus/9026000424/record/documents/petition.txt`
- `metrics/statpack.md` and `schemas/{prediction,agent_tooling,agent_flags}.schema.json`

## 3. Corpus Queries (`fedcourts query`)

1. **`uv run fedcourts query --court scotus --era 2020s --limit 15`**
   - **Transfer:** `ranged corpus reads: 12 GET(s), 3080192 byte(s)`
   - **Result:** Retrieved 15 recent 2020s SCOTUS dispositions (`25-944`, `26-239`, `26-6095`, `26A661`, `26A658`, `26A657`, `25-442`, `25-1348`, `25-7515`, `25-7522`, `25-7555`, `25-1411`, `25-7656`, `25-1426`, `26-18`), confirming recent OT2026 conference grant/GVR vs. denial patterns and multi-distribution profiles on granted cases.
2. **`uv run fedcourts query --court scotus --citation "593 U.S. 67" --limit 10`**
   - **Transfer:** `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - **Result:** 0 rows returned (`note: citations filter: only 195 row(s) in scope (scotus) carry any reporter citation at all...`); verified *AMG Capital* (`593 U.S. 67`) via CourtListener MCP instead as recommended by the CLI note.
3. **`uv run fedcourts query --court scotus --judge Wilkinson --judge King --judge Thacker --limit 10`**
   - **Transfer:** `ranged corpus reads: 743 GET(s), 194641920 byte(s)`
   - **Result:** 0 SCOTUS rows (panel judge names are not populated on SCOTUS rows).
4. **`uv run fedcourts query --court ca4 --judge Wilkinson --judge King --judge Thacker --limit 10`**
   - **Transfer:** `ranged corpus reads: 92 GET(s), 24117248 byte(s)`
   - **Result:** 0 resolved `ca4` rows with all three judges simultaneously indexed in the resolved corpus slice.
5. **`uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`**
   - **Transfer:** `ranged corpus reads: 38 GET(s), 9895936 byte(s)`
   - **Result:** Retrieved 10 recent granted SCOTUS cases (`25-944`, `26-239`, `26A560`, `25-1408`, `26A512`, `26-12`, `26-204`, `26A476`, `25-1103`, `25-7026`), including Fourth Circuit grants (`25-1408`, `26-12`), confirming counselled circuit-split / government-petition characteristics and `distribution_count >= 2` on almost all granted cert petitions.
6. **`uv run fedcourts query --court scotus --disposition granted --era 2020s --include-open --limit 40`**
   - **Transfer:** `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   - **Result:** Checked 40 recent/open granted SCOTUS cases across OT2025–OT2026 to verify whether any pending merits case involves Rule 60(b), nonparty appellate standing (*Devlin*), or FTC Act § 13(b) receiverships that could prompt a hold and GVR. None exists.

*(Note: One exploratory call with `--originating-court ca4` exited immediately with CLI usage code 2 without corpus reads because `--originating-court` is not a `fedcourts query` flag.)*

## 4. External Legal Research (CourtListener MCP Server)

1. **`mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `case_name="Pukke"`):** Located the Fourth Circuit's published decisions in the underlying Sanctuary Belize litigation, including *FTC v. Andris Pukke* (*Pukke I*), 53 F.4th 80 (4th Cir. 2022), and *FTC v. Andris Pukke* (*Pukke II*), No. 23-1742 (4th Cir. Dec. 12, 2024) (`cluster_id: 10292796`, `opinion_id: 10759384`).
2. **`mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `case_name="Yu Lin"`):** Located *Federal Trade Commission v. Yu Lin*, 66 F.4th 164 (4th Cir. Apr. 18, 2023) (`cluster_id: 9392721`, `opinion_id: 9388197`), affirming the denial of an untimely post-judgment motion to intervene and Rule 60(b) motion by 14 Sanctuary Belize / NLG investors.
3. **`mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `q=""Sanctuary Belize""`):** Confirmed all 8 Fourth Circuit opinions referencing the Sanctuary Belize enforcement litigation.
4. **`mcp_courtlistener_search` (`type="d"` and `type="o"`, `court="scotus"`, `q="Pukke OR "Yu Lin" OR "Sanctuary Belize""`):** Checked for any related SCOTUS dockets/opinions indexed under those terms (0 full-opinion matches; verified *Pukke v. FTC*, 144 S. Ct. 73 (2023) cert denial via `analyze_citations`).
5. **`mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=72251389`):** Checked docket entries on Fourth Circuit No. 26-1130 (*In re: Beckie Boddie*), confirming no post-judgment rehearing petition was filed.
6. **`mcp_courtlistener_search` (`type="r"` and `type="rd"`, `court="mdd"`, `docket_number="1:18-cv-03309"`):** Located District of Maryland RECAP docket `14527299` (*In re Sanctuary Belize Litigation*) and reviewed docket entries from September 2024 through April 2026 (`ECF Nos. 1540, 1541, 1543, 1547, 1549, 1562, 1563, 1581, 1587, 1588, 1603, 1605, 1607, 1612, 1613`).
7. **`mcp_courtlistener_read_document` & `mcp_courtlistener_search_document` (`opinion_id: 9388197`, `opinion_id: 10759384`, `recap_document_id: 439461627`):**
   - Read *FTC v. Yu Lin*, 66 F.4th 164 (4th Cir. 2023) (`9388197`), on untimely post-judgment third-party intervention in the Sanctuary Belize receivership.
   - Read *FTC v. Pukke*, No. 23-1742 (4th Cir. Dec. 12, 2024) (`10759384`), confirming that Judges Wilkinson, King, and Thacker upheld the post-*AMG Capital* continuation of the Sanctuary Belize receivership and asset freeze both as ancillary to Section 13(b) permanent injunctions and to enforce the $120.2 million *AmeriDebt* civil contempt sanction.
   - Read Judge Paula Xinis's May 13, 2025 Memorandum Opinion and Order (`ECF No. 1587`, `recap_document_id: 439461627`), denying third-party bidder Bob Yari's counselled Rule 24 motion to intervene after a full hearing on the day of the $20.5 million `FBIM` Sale Order (`ECF No. 1588`).
8. **`mcp_courtlistener_analyze_citations`:** Verified all 7 key case citations (*Devlin v. Scardelletti*, 536 U.S. 1 (2002); *Marino v. Ortiz*, 484 U.S. 301 (1988); *Bowles v. Russell*, 551 U.S. 205 (2007); *AMG Capital Mgmt., LLC v. FTC*, 593 U.S. 67 (2021); *Pukke v. FTC*, 144 S. Ct. 73 (2023); *FTC v. Pukke*, 53 F.4th 80 (4th Cir. 2022); *FTC v. Yu Lin*, 66 F.4th 164 (4th Cir. 2023)) — 7 of 7 verified in CourtListener.
