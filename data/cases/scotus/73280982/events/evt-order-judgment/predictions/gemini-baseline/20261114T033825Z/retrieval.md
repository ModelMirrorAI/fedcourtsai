# Retrieval Log

All retrievals consulted beyond the provisioned case inputs (`data/cases/scotus/73280982/record/`, `event.yaml`, `schemas/*.json`, and `metrics/statpack.md` / `metrics/statpack.json` / `metrics/README.md`):

## 1. Local Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --help`
   - Result: Printed CLI flag documentation; no corpus reads.
2. `uv run fedcourts query --court scotus --stage merits --citation "15 U.S.C. § 77k" --citation "601 U.S. 257" --citation "575 U.S. 175" --decided-before 2026-11-14 --limit 25 --json`
   - Result: Failed (`Exit Code: 2`, `No such option: --stage`); no corpus reads.
3. `uv run fedcourts query --court scotus --stage merits --judge "Milan D. Smith" --judge "Rawlinson" --judge "Rakoff" --decided-before 2026-11-14 --limit 25 --json`
   - Result: Failed (`Exit Code: 2`, `No such option: --stage`); no corpus reads.
4. `uv run fedcourts query --court scotus --stage merits --party "Securities" --originating-circuit ca9 --decided-before 2026-11-14 --limit 20 --json`
   - Result: Failed (`Exit Code: 2`, `No such option: --stage`); no corpus reads.
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-11-14 --limit 30 --full`
   - `ranged corpus reads: 62 GET(s), 16187392 byte(s)`
   - Result: Returned 30 recent 2020s SCOTUS `granted` rows (cert grants and interim applications through `2026-11-13`, confirming no post-grant activity on `scotus/73280982` and showing companion OT2026 grants).
6. `uv run fedcourts query --court scotus --citation "601 U.S. 257" --citation "598 U.S. 651" --citation "575 U.S. 175" --citation "604 U.S. 4" --citation "604 U.S. 20" --decided-before 2026-11-14 --limit 10 --full`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 0 rows (note explained only 195 SCOTUS rows carry own-case reporter citations in the corpus).
7. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-08-01 --limit 80 --full`
   - `ranged corpus reads: 58 GET(s), 15204352 byte(s)`
   - Result: Returned 80 SCOTUS `granted` rows prior to `2026-08-01`, including resolved OT2025 merits decisions and their `merits_judgment` labels (`vacated`, `reversed`, `affirmed`) such as *Hikma v. Amarin* (`24-889`), *Sripetch v. SEC* (`25-466`), *Cisco Systems v. Doe I* (`24-856`), *Havana Docks* (`24-983`), and *Chatrie* (`25-112`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""15 U.S.C. 77k" OR "Section 11" "registration statement" "misleading" OR "Macquarie Infrastructure""`, `fields=["caseName","citation","dateFiled","judge","cluster_id","opinions","docketNumber"]`, `num_results=20`)
   - Result: `count: 61`; returned *Macquarie Infrastructure Corp. v. Moab Partners, L. P.* (`601 U.S. 257`, `opinion_id=11066691`), *Slack Technologies, LLC v. Pirani* (`598 U.S. 759`, `opinion_id=10516281`), *Omnicare, Inc. v. Laborers Dist. Council Constr. Industry Pension Fund* (`575 U.S. 175`, `opinion_id=2788684`), *CalPERS v. ANZ Securities* (`582 U.S. 497`), *Lorenzo* (`587 U.S. 71`), etc.
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q="*"`, `filed_after="2026-10-01"`, `filed_before="2026-11-14"`, `fields=["caseName","citation","dateFiled","judge","cluster_id","opinions","docketNumber"]`, `num_results=20`)
   - Result: `count: 2`; returned two OT2026 order-related opinions (*Mullin v. Friends of the Ruidosa Church* and *FCC v. Brown*).
3. `mcp_courtlistener_read_document` (`opinion_id=11066691`, `chunk_index=0`, `chunk_size=15000`)
   - Result: Read syllabus and procedural posture of *Macquarie Infrastructure Corp. v. Moab Partners, L. P.*, 601 U.S. 257 (2024) (Sotomayor, J., 9–0, vacating and remanding).
4. `mcp_courtlistener_read_document` (`opinion_id=10516281`, `chunk_index=0`, `chunk_size=15000`)
   - Result: Read syllabus and procedural posture of *Slack Technologies, LLC v. Pirani*, 598 U.S. 759 (2023) (Gorsuch, J., 9–0, vacating and remanding Ninth Circuit Section 11 decision).
5. `mcp_courtlistener_search_document` (`opinion_id=[11066691, 10516281, 2788684]`, `query="It is so ordered"`, `snippet_size=600`)
   - Result: Verified exact judgment lines of *Macquarie* (`vacated`), *Slack* (`vacated`), and *Omnicare* (`vacate the judgment below and remand`).
6. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Amalgamated Bank" OR "Ohman" OR "Amarin Pharma""`, `fields=["caseName","citation","dateFiled","judge","cluster_id","opinions","docketNumber"]`, `num_results=10`)
   - Result: `count: 33`; returned *Facebook, Inc. v. Amalgamated Bank* (`604 U.S. 4`, DIG), *NVIDIA Corp. v. E. Ohman J:or Fonder AB* (`604 U.S. 20`, DIG), and *Hikma Pharmaceuticals USA Inc. v. Amarin Pharma, Inc.* (`2026-06-04`, `opinion_id=11337517`).
7. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""dismissed as improvidently granted""`, `filed_after="2025-10-01"`, `filed_before="2026-09-30"`, `fields=["caseName","citation","dateFiled","judge","cluster_id","opinions","docketNumber"]`, `num_results=30`)
   - Result: `count: 1`; returned *Hamm v. Smith* (`2026-05-21`, GVR opinion referencing prior DIG).
8. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Goldman Sachs" "Arkansas Teacher" OR "Lorenzo v. Securities" OR "Morrison""`, `fields=["caseName","citation","dateFiled","judge","cluster_id","opinions","docketNumber"]`, `num_results=15`)
   - Result: `count: 23`; returned *Goldman Sachs Group, Inc. v. Arkansas Teacher Retirement System* (`594 U.S. 113`, `opinion_id=4697201`).
9. `mcp_courtlistener_read_document` (`opinion_id=11337517`, `chunk_index=0`, `chunk_size=12000`)
   - Result: Read syllabus of *Hikma Pharmaceuticals USA Inc. v. Amarin Pharma, Inc.* (June 4, 2026) to compare why *Hikma* reversed outright (evaluating complaint sufficiency itself on a single claim) whereas *Macquarie*/*Slack*/*Omnicare* vacated and remanded.
10. `mcp_courtlistener_search_document` (`opinion_id=[11337517, 4697201]`, `query="It is so ordered"`, `snippet_size=600`)
    - Result: Confirmed judgment lines of *Hikma* (`reversed`) and *Goldman Sachs* (`vacated`).
11. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Sripetch" OR "Havana Docks" OR "Cisco Systems""`, `fields=["caseName","citation","dateFiled","judge","cluster_id","opinions","docketNumber"]`, `num_results=10`)
    - Result: `count: 26`; returned *Sripetch v. SEC* (`cluster_id=10870059`, June 4, 2026), *Havana Docks* (`2026-05-21`), and *Cisco Systems* (`2026-06-23`).
12. `mcp_courtlistener_search_document` (`opinion_id=[11337517]`, `query="delivered the opinion of the Court"`, `snippet_size=300`)
    - Result: Confirmed Justice Jackson authored *Hikma v. Amarin* (unanimous).
13. `mcp_courtlistener_call_endpoint` (`endpoint_id="clusters"`, `query={"id": 10870059, "fields": ["id", "case_name", "judges", "sub_opinions"]}`)
    - Result: Confirmed Justice Gorsuch authored *Sripetch v. SEC* (single unanimous opinion).

## 3. Web Searches

None attempted.
