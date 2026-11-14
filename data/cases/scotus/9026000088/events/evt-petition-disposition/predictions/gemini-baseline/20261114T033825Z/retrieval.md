# Retrieval Log — `scotus/9026000088` (`evt-petition-disposition`, `20261114T033825Z`)

Mode: `forward` (`context.mode = "forward"`, `DECIDED_BEFORE` unset). No forecast of this case was sought or surfaced.

## 1. Corpus Queries (`fedcourts`)

1. Path and CLI check:
   - Command: `uv run fedcourts paths --court "scotus" --docket "9026000088" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Result: Resolved `case_id = scotus/9026000088`, `corpus = corpus/corpus.db`, `event = data/cases/scotus/9026000088/events/evt-petition-disposition/event.yaml`; printed `fedcourts query` flag options.

2. Recent 2020s SCOTUS denied and granted priors:
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer stderr: `ranged corpus reads: 11 GET(s), 2818048 byte(s)`
   - Result: Returned 10 recent OT2026 denied SCOTUS rows (cert petitions and applications).
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)` (part of combined shell invocation; 10 granted OT2026 rows returned).

3. Attempted counsel filter (failed usage check):
   - Command: `uv run fedcourts query --court scotus --attorney "Owen Dennis Yeates" --limit 20`
   - Result: Exit code 2 (`No such option: --attorney`); listed supported structured filter flags.

4. Specific campaign-finance disclosure prior dockets (`25-1248` and `23-926`):
   - Command: `uv run fedcourts query --court scotus --docket-number 25-1248`
   - Transfer stderr: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: Returned `scotus/73292884` (*Rio Grande Foundation v. Maggie Toulouse Oliver*), `disposition: "denied"`, `date_cert_denied: "2026-10-05"`, `distribution_count: 2`, `has_opinion: false`.
   - Command: `uv run fedcourts query --court scotus --docket-number 23-926`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72483395` (*No on E, San Franciscans Opposing the Affordable Housing Production Act, et al. v. David Chiu, et al.*), `disposition: "denied"`, `date_cert_denied: "2024-10-07"`, `distribution_count: 2`, `has_opinion: false`.

5. Specific campaign-finance disclosure prior dockets (`26A349` and `23-1316`):
   - Command: `uv run fedcourts query --court scotus --docket-number 26A349 --include-open --include-applications`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/9526000349` (*Americans for Prosperity Foundation, et al. v. Anthony Albence, et al.*), `disposition: "denied"`, `date_decided: "2026-10-01"`, `response_requested: true`, `referred_to_court: true`, `has_opinion: false`.
   - Command: `uv run fedcourts query --court scotus --docket-number 23-1316`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72479625` (*Doug Smith, et al. v. Richard Stillie, Jr., in His Official Capacity as Chair, Alaska Public Offices Commission, et al.*), `disposition: "denied"`, `date_cert_denied: "2024-11-18"`, `distribution_count: 6`, `has_opinion: false`.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Alaska Policy Forum v. Alaska Public Offices Commission"`):
   - Returned 1 result: `cluster_id = 10793811`, `opinion_id = 11260453`, Alaska Supreme Court (`alaska`), Docket `S18533`, filed `2026-02-13`.
2. `mcp_courtlistener_search` (`type="o"`, `case_name="No on E v. Chiu"`):
   - Returned 2 Ninth Circuit opinion clusters (`cluster_id = 9473501`, `9835966`).
3. `mcp_courtlistener_search` (`type="o"`, `case_name="Rio Grande Foundation v. Oliver"`):
   - Returned 3 Tenth Circuit / D.N.M. opinion clusters (including `cluster_id = 10668506`, 10th Cir. Sept. 9, 2025).
4. `mcp_courtlistener_read_document` (`opinion_id=11260453`, `chunk_index=[2..11]`, `chunk_size=10000`):
   - Returned `"error": "No text is available for this document."`
5. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10793811`, with `Procedural_history`):
   - Returned field-name validation error (`Invalid fields: ['Procedural_history']. Did you mean: procedural_history?`).
6. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10793811`, with valid lowercase fields):
   - Returned cluster `10793811` confirming single sub-opinion `11260453` (`2026-02-13`) and empty text/summary metadata.
7. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q='"No on E" OR "Gaspee Project" OR "Smith v. Helzer" OR "Rio Grande Foundation" OR "Wyoming Gun Owners"'`):
   - Returned `count: 0` (confirming no separate SCOTUS opinions on those cert denials).
8. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `q='"Smith v. Helzer" OR "No on E" OR "Gaspee Project" OR "Rio Grande Foundation" OR "Wyoming Gun Owners"'`):
   - Returned `count: 0` (consistent with thin SCOTUS docket coverage on CourtListener).
9. `mcp_courtlistener_search` (`type="o"`, `case_name="Americans for Prosperity Foundation v. Meyer"`):
   - Returned `count: 0`.
10. `mcp_courtlistener_search` (`type="o"`, `case_name="Institute for Free Speech"`, `court=["scotus","ca3","ca9","ca10","ca1"]`, `filed_after="2023-01-01"`):
    - Returned `count: 0`.

## 3. Web Searches (`google_web_search`)

1. `query: '"Smith v. Helzer" "certiorari" OR "Supreme Court"'`:
   - Confirmed *Smith v. Stillie* (below: *Smith v. Helzer*, 95 F.4th 1207 (9th Cir. 2024)), No. 23-1316, cert. denied Nov. 18, 2024, 145 S. Ct. 567.
2. `query: '"No on E" "Chiu" "certiorari" OR "Supreme Court"'`:
   - Confirmed *No on E v. Chiu*, No. 23-926 (below: 85 F.4th 493 (9th Cir. 2023)), cert. denied Oct. 7, 2024.
3. `query: '"Rio Grande Foundation v. Oliver" "certiorari" OR "Supreme Court"'`:
   - Confirmed *Rio Grande Foundation v. Oliver*, No. 25-1248 (below: 154 F.4th 1213 (10th Cir. 2025)), cert. denied Oct. 5, 2026.
4. `query: 'site:law.justia.com "Alaska Policy Forum" "7801" "Borghesan"'`:
   - Confirmed Alaska Supreme Court Opinion No. 7801 (583 P.3d 701, Feb. 13, 2026), authored by Justice Borghesan, affirming the Superior Court and APOC.
5. `query: '"No on E" "23-926" "Thomas" OR "Alito" OR "Gorsuch" OR "Kavanaugh" "certiorari"'`:
   - Confirmed no noted dissents from denial of certiorari in No. 23-926 (with Gorsuch and Kavanaugh recused) despite nine Ninth Circuit judges dissenting from denial of rehearing en banc.
6. `query: '"Rio Grande Foundation v. Oliver" "25-1248" "Response Requested" OR "DISTRIBUTED" OR "dissent"'`:
   - Confirmed May 26, 2026 `Response Requested` after New Mexico's initial waiver, Judge Eid's Tenth Circuit dissent on donor earmarking, redistribution for the Sept. 28, 2026 Long Conference, and Oct. 5, 2026 cert denial with no noted SCOTUS dissents.
7. `query: '"Wyoming Gun Owners v. Gray" "certiorari" OR "Supreme Court"'`:
   - Confirmed no cert petition was filed/granted in *Wyoming Gun Owners v. Gray*, 83 F.4th 1224 (10th Cir. 2023), and surfaced docket number `26A349` (*Americans for Prosperity Foundation v. Albence*).
8. `query: 'site:law.justia.com "Alaska Policy Forum" "7801" "AFFIRMED" OR "dissenting" OR "concurring"'`:
   - Confirmed unanimous 5–0 affirmance by the Alaska Supreme Court (Maassen, C.J., and Carney, Borghesan, Henderson, and Pate, JJ.) with no dissenting or concurring opinions.
