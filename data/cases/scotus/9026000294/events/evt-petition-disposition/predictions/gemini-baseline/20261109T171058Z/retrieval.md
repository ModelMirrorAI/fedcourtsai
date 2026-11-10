# Retrieval Log

## 1. `fedcourts` CLI Calls

- `uv run fedcourts paths --court "scotus" --docket "9026000294" --event "evt-petition-disposition" --role predictor`
  - Returned case paths (`case_id: scotus/9026000294`, `corpus: corpus/corpus.db`, `event: data/cases/scotus/9026000294/events/evt-petition-disposition/event.yaml`).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
  - `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
  - Returned 10 recent OT2026 granted SCOTUS rows for cert-stage comparison.
- `uv run fedcourts query --court scotus --docket-number 26-292`
  - `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
  - Returned the open companion row for *Fiona Havlish, et al. v. The Taliban, et al.*, No. 26-292 (`scotus/9026000292`, `distribution_count: 2`, `distributed_for_conference: 2026-11-13`).
- `uv run fedcourts query --court scotus --docket-number 26-293`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Returned the open companion row for *Kathleen Ashton, et al. v. The Taliban, et al.*, No. 26-293 (`scotus/9026000293`, `distribution_count: 2`, `distributed_for_conference: 2026-11-13`).
- `uv run fedcourts query --court scotus --citation "598 U.S. 264" --citation "560 U.S. 305" --citation "583 U.S. 202" --limit 10`
  - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
  - Returned 0 rows (with note that only 200 rows in scope carry parallel reporter citations).
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Returned 5 recent OT2026 denied SCOTUS cert petitions (`26-18`, `26-55`, `26-85`, `26-87`, `26-107`).
- `uv run fedcourts query --court scotus --era 2020s --disposition cvsg --limit 5`
  - Failed with exit code 2 (`Unknown disposition 'cvsg'; choose one of: granted, denied, granted-in-part, gvr, summary-reversal, dismissed, withdrawn, other`).

## 2. CourtListener MCP Calls

- `mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `case_name="Havlish v. Taliban"`, `fields=["caseName", "citation", "dateFiled", "docketNumber", "cluster_id", "opinions", "judge"]`)
  - Returned 2 clusters for the Second Circuit decisions below in *Havlish v. Taliban; Aliganga v. Taliban*:
    1. Panel opinion filed `2025-08-26` (`cluster_id: 10660852`, `opinion_id: 11127439`, 152 F.4th 339).
    2. En banc denial order and opinions filed `2026-03-19` (`cluster_id: 10804556`, `opinion_id: 11277807`, 170 F.4th 100).
- `mcp_courtlistener_read_document` (`opinion_id=11127439`, `chunk_index=[0, 1]`, `chunk_size=8000`)
  - Read the opening sections of Judge Cabranes's panel majority opinion in *Havlish v. Taliban; Aliganga v. Taliban* (2d Cir. Aug. 26, 2025).
- `mcp_courtlistener_read_document` (`opinion_id=11277807`, `chunk_index=[0, 1, 2]`, `chunk_size=8000`)
  - Read the en banc order and the first sections of Judge Sullivan's dissent from denial of rehearing en banc (joined by Chief Judge Livingston and Judges Bianco and Park).
- `mcp_courtlistener_read_document` (`opinion_id=11127439`, `chunk_index=[4, 5, 6, 7]`, `chunk_size=8000`)
  - Read the panel majority's FSIA analysis on recognition of Afghanistan and DAB's status as an agency or instrumentality under 28 U.S.C. § 1603(b)(2).
- `mcp_courtlistener_read_document` (`opinion_id=11277807`, `chunk_index=[3, 4, 5, 6, 7]`, `chunk_size=8000`)
  - Read the remainder of Judge Sullivan's en banc dissent and the first half of Judge Menashi's opinion concurring in part and dissenting in part from the denial of rehearing en banc.
- `mcp_courtlistener_read_document` (`opinion_id=11277807`, `chunk_index=[8, 9, 10]`, `chunk_size=8000`)
  - Read the remainder of Judge Menashi's en banc dissent and the joint statement of Judges Cabranes, Calabresi, Nardini, and Lohier respecting the denial of rehearing en banc.
- `mcp_courtlistener_read_document` (`opinion_id=11127439`, `chunk_index=[8, 9, 13, 14, 15]`, `chunk_size=8000`)
  - Read the panel majority's TRIA analysis and the first sections of Judge Sullivan's panel dissent.
- `mcp_courtlistener_read_document` (`opinion_id=11127439`, `chunk_index=[17, 18, 19]`, `chunk_size=8000`)
  - Read the concluding sections of Judge Sullivan's panel dissent on § 1603(b)(2), § 1611(b)(1), and TRIA § 201(a).

## 3. Web Searches

- None.
