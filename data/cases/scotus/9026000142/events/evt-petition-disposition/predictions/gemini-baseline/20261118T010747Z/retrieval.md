# Retrieval Log

Beyond the provisioned inputs under `data/cases/scotus/9026000142/`, `metrics/statpack.md`, `metrics/statpack.json`, `metrics/amicus-line.json`, `metrics/claim-scores.json`, and `docs/outcome-decomposition.md`, the following external/corpus lookups were attempted during this run:

## 1. Corpus CLI Lookups (`uv run fedcourts query`)

1. **Companion petition `26-141` (*Donald J. Trump v. E. Jean Carroll*)**:
   - Command: `uv run fedcourts query --court scotus --docket-number 26-141`
   - Transfer stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned open row `scotus/9026000141` (`Donald J. Trump v. E. Jean Carroll`), filed `2026-07-30`, `distributed_for_conference: "2026-12-04"`, `distribution_count: 1`, `parties: ["David Boyle", "E. Jean Carroll", "President Donald J. Trump"]`.

2. **Prior *Carroll II* petition `25-573` (*Donald J. Trump v. E. Jean Carroll*)**:
   - Command: `uv run fedcourts query --court scotus --docket-number 25-573`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned resolved row `scotus/73279019`, filed `2025-11-13`, `distribution_count: 16`, `disposition: "denied"`, `date_decided: "2026-06-29"`, `has_opinion: false`.

3. **Precedent reporter-citation lookup (`549 U.S. 225`, `515 U.S. 417`, `603 U.S. 593`)**:
   - Command: `uv run fedcourts query --court scotus --citation "549 U.S. 225" --citation "515 U.S. 417" --citation "603 U.S. 593"`
   - Transfer stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Empty result with CLI note that only 195 rows in `scotus` populate `citations` (switched to CourtListener MCP for precedent verification).

4. *(Aborted Python wrapper shell call)*:
   - Attempted a `python3 -c` wrapper to run 2020s `denied`/`granted`/`gvr` corpus queries; failed immediately at Python parse time (`SyntaxError`) before invoking `fedcourts`. Re-issued cleanly via heredoc below.

5. **2020s SCOTUS `denied` priors**:
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 300`
   - Transfer stderr: `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
   - Result: 300 resolved rows (including `26-210`, *Trump v. Thakur*, denied `2026-11-16` at `distribution_count: 1`).

6. **2020s SCOTUS `granted` priors**:
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 100`
   - Transfer stderr: `ranged corpus reads: 57 GET(s), 14942208 byte(s)`
   - Result: 100 resolved rows (including 8 United States / Presidential petitions showing distribution counts 0–3).

7. **2020s SCOTUS `gvr` priors**:
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 100`
   - Transfer stderr: `ranged corpus reads: 105 GET(s), 27525120 byte(s)`
   - Result: 100 resolved rows (including `25-551`, *United States v. Shaheem Johnson*, `distribution_count: 2`, and `24-1177`, *A.A.R.P. v. Trump*).

8. **SCOTUS priors with Judge Menashi on panel below**:
   - Command: `uv run fedcourts query --court scotus --judge Menashi --limit 10`
   - Transfer stderr: `ranged corpus reads: 743 GET(s), 194772992 byte(s)`
   - Result: 0 matching rows (panel metadata not populated on matching SCOTUS cert rows).

9. **Recent Administration cert denial `26-210` (*Trump v. Thakur*)**:
   - Command: `uv run fedcourts query --court scotus --docket-number 26-210`
   - Transfer stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned `scotus/9026000210`, filed `2026-08-19` by Solicitor General D. John Sauer, `distribution_count: 1`, `disposition: "denied"` on `2026-11-16`, `has_opinion: false`.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", case_name="Trump v. Carroll", filed_after="2026-06-01", filed_before="2026-07-01", fields=["caseName","citation","dateFiled","docketNumber","judge","snippet","cluster_id","opinions"])` -> `count: 0` (checked whether any separate opinion accompanied the June 29, 2026 *Carroll II* cert denial).
2. `mcp_courtlistener_search(type="o", court="scotus", citation="549 U.S. 225", fields=["caseName","citation","dateFiled","judge","cluster_id"])` -> `count: 1` (*Osborn v. Haley*, `cluster_id: 145762`, `2007-01-22`).
3. `mcp_courtlistener_search(type="o", court="scotus", docket_number="25-573", fields=["caseName","citation","dateFiled","docketNumber","judge","snippet"])` -> `count: 0` (confirmed no separate opinion indexed on *Carroll II* cert denial).
4. `mcp_courtlistener_search(type="o", court="scotus", citation="515 U.S. 417", fields=["caseName","citation","dateFiled","judge","cluster_id"])` -> `count: 2` (*Gutierrez de Martinez v. Lamagno*, `cluster_id: 117955`, `1995-06-14`).
5. `mcp_courtlistener_search(type="o", court="scotus", citation="603 U.S. 593", fields=["caseName","citation","dateFiled","judge","cluster_id"])` -> `count: 5` (*Trump v. United States*, `cluster_id: 10600038`, `2024-07-01`).
6. `mcp_courtlistener_search(type="o", court="scotus", citation="146 S. Ct. 2789", fields=["caseName","citation","dateFiled","docketNumber","judge","snippet"])` -> `count: 0` (confirmed `146 S. Ct. 2789` *Carroll II* denial was a bare memorandum order with no published dissent).

## 3. Web Searches
None attempted.
