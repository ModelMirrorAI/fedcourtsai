# Retrieval Log

Mode: `forward` (`DECIDED_BEFORE` unset; `cutoff: 2026-10-02` bounds the provisioned baseline only).

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 8 GET(s), 2031616 byte(s)`
   - Purpose: Inspect recent OT2026 SCOTUS dispositions, salience scores, and active counsel (confirming current Solicitor General D. John Sauer and recent OT2026 order-list patterns).
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`
   - Purpose: Examine recent OT2026 SCOTUS certiorari grants, distribution counts (`2`–`5`), and amicus participation patterns.
3. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Check recent OT2026 GVR dispositions to confirm none involve ERISA § 502(a)(2) or FAA effective vindication.
4. `uv run fedcourts query --citation "552 U.S. 248" --citation "473 U.S. 134" --citation "590 U.S. 538" --limit 10`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Purpose: Probe corpus parallel-citation index for *LaRue*, *Russell*, and *Thole* (returned 0 rows, noting corpus `citations` holds own parallel cites rather than a citing-cases graph).

## 2. CourtListener MCP Queries

- **Initial failed `call_endpoint` attempts (schema filter syntax):**
  - `call_endpoint(endpoint_id="dockets", query={"case_name__icontains": "Trauernicht", "fields": "id,court,case_name,docket_number,date_filed,date_terminated"})` -> failed validation (`case_name__icontains` extra input not permitted on `DocketsEndpoint`).
  - `call_endpoint(endpoint_id="dockets", query={"case_name__icontains": "Tenneco", "court": "scotus", "fields": "id,court,case_name,docket_number,date_filed,date_terminated"})` -> failed validation (`case_name__icontains` extra input not permitted on `DocketsEndpoint`).
  - `get_endpoint_schema(endpoint_id="docket-entries")` -> retrieved valid filter/ordering schema (`docket`, `order_by="-date_filed"`).
- **Fourth Circuit split opinion (*Trauernicht v. Genworth Financial Inc.*):**
  - `search(type="o", case_name="Trauernicht v. Genworth")` -> located `cluster_id: 10807488`, `opinion_id: 11274227` (4th Cir. No. 24-1880, filed March 10, 2026).
  - `read_document(opinion_id=11274227, chunk_index=[0,1,2,3])` and `read_document(opinion_id=11274227, chunk_index=[4,5,6,7])` -> read the full opinion of Judge Richardson reversing Rule 23(b)(1) class certification, confirming its explicit break with the arbitration circuits under *Russell*, *LaRue*, and *Thole*, while verifying its distinct Rule 23 procedural posture.
- **SCOTUS opinion/docket searches for prior or companion ERISA § 502(a)(2) split cases:**
  - `search(type="o", court="scotus", q='"Cedeno" "Sasson" OR "Parker" "Tenneco" OR "Platt" "Sodexo" OR "Parrott" "International Bancshares" OR "Williams" "Shapiro"')` -> 0 results.
  - `search(type="d", court="scotus", q='"Envision Management" OR "Wilmington Trust" OR "Sasson" OR "Tenneco" OR "Sodexo" OR "International Bancshares" OR "Genworth Financial"')` -> 0 results.
  - `search(type="o", court="scotus", q='("Argent Trust" AND "Cedeno") OR ("Sasson" AND "Cedeno") OR ("Tenneco" AND "Parker") OR ("Envision Management") OR ("Wilmington Trust" AND "Henry") OR ("Sodexo" AND "Platt") OR ("Trauernicht") OR ("Genworth")')` -> 3 unrelated older results.
  - `search(type="o", court="scotus", case_name=...)` for `"Cedeno"` (10 older results), `"Tenneco"` (17 older results), `"Envision"` (0 results), `"Sodexo"` (0 results).
  - `search(type="d", court="scotus", case_name=...)` for `"Argent Trust"`, `"Envision Management"`, `"Wilmington Trust"`, `"Trauernicht"` -> 0 results each.
- **Companion appellate and district dockets in the 1–7 circuit split:**
  - `search(type="r", case_name="Trauernicht")` -> located `ca4` `docket_id=69207877` (No. 24-1880) and `vaed` `docket_id=64884320` (No. 3:22-cv-00532).
  - `call_endpoint(endpoint_id="docket-entries", docket=69207877)` & `docket=64884320` -> confirmed rehearing en banc was denied without a poll on June 4–5, 2026, mandate issued June 12, 2026, and the *Trauernicht* plaintiffs filed no certiorari petition before their September 2, 2026 deadline.
  - `search(type="r", case_name="Cedeno v. Sasson")` (0 results), `search(type="o", case_name="Cedeno v. Sasson")` (`ca2` `docket_id=66782109`), `search(type="r", case_name="Cedeno v. Argent Trust")` (`ca2` `66782109`, `nysd` `18694619`), and `call_endpoint(endpoint_id="docket-entries", docket=66782109 & 18694619)` -> confirmed ongoing S.D.N.Y. district-court proceedings through October 2026.
  - `search(type="o", case_name="Parker v. Tenneco")` (`ca6` `68104408`), `search(type="r", case_name="Parker v. Tenneco")` (`ca6` `69060803`/`68104408`, `mied` `67223869`), and `call_endpoint(endpoint_id="docket-entries", docket=68104408 & 67223869)` -> confirmed active E.D. Mich. proceedings through November 10, 2026.
  - `search(type="r", case_name="Platt v. Sodexo")` (`ca9` `68320288`, `cacd` `66622807`) and `call_endpoint(endpoint_id="docket-entries", docket=68320288 & 66622807)` -> noted U.S. Secretary of Labor appellate amicus participation in 2024 and active C.D. Cal. trial-prep proceedings through November 12, 2026.
  - `search(type="o", case_name="Williams v. Shapiro")` (`ca11` `69021859`) and `call_endpoint(endpoint_id="docket-entries", docket=69021859)` -> confirmed December 15, 2025 Eleventh Circuit affirmance.
  - `search(type="r", case_name="Parrott v. International Bancshares")` (0 results), `search(type="o", court="ca5", case_name="Bancshares")` (15 older results), `search(type="o", court="ca5", case_name="Parrott")` (`ca5` `71166303`), `search(type="d", case_name="Parrott v. International Bancshares")` (0 results), `search(type="d", court="txwd", case_name="Parrott")` (`txwd` `69342290`), and `call_endpoint(endpoint_id="docket-entries", docket=71166303 & 69342290)` -> confirmed active W.D. Tex. severability proceedings before Judge Ezra through October–November 2026 with no pending SCOTUS petition.

## 3. Web / Official `supremecourt.gov` Lookups

- `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-267.html` and `https://www.supremecourt.gov/RSS/Cases/JSON/26-267.json` (permitted in `forward` mode):
  - Verified No. 26-267 remains genuinely pending (`RelatedCaseNumber: []`) with two post-snapshot entries: (1) `Oct 15 2026`: Respondent's response deadline extended to December 2, 2026; and (2) `Nov 02 2026`: Brief amici curiae of The American Benefits Council, The Committee on Investment of Employee Benefit Assets, and The ERISA Industry Committee filed.
- `google_web_search` with `site:supremecourt.gov` filters:
  1. `site:supremecourt.gov "Trauernicht" OR "Genworth Financial"`
  2. `site:supremecourt.gov "Cedeno" "Sasson" OR "Parker" "Tenneco" OR "Platt" "Sodexo"`
  3. `site:supremecourt.gov "Parrott" "International Bancshares" OR "Williams" "Shapiro"`
  - Confirmed no companion Supreme Court petition in *Trauernicht* or *Parrott* (only references inside No. 26-267's filings). Note: Google's search synthesizer included an unopened `scotusgate.com` grounding link alongside factual docket dates for No. 26-267; no forecast, odds, or third-party opinion surfaced, the link was never visited, and this is disclosed at `info` level in `flags.json`.
