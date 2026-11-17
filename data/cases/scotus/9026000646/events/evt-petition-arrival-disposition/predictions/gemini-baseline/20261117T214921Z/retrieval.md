# Retrieval Log (`scotus/9026000646`, `evt-petition-arrival-disposition`)

Mode: `forward` (`DECIDED_BEFORE` unset; `context.json` `mode: "forward"`).

## 1. Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000646" --event "evt-petition-arrival-disposition" --role predictor`
   - Transfer line: none (`paths` helper).
   - Result: Confirmed `case_id = scotus/9026000646`, `corpus = corpus/corpus.db`, `event = data/cases/scotus/9026000646/events/evt-petition-arrival-disposition/event.yaml`.

2. `uv run fedcourts query --court scotus --era 2020s --limit 15`
   - Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned 15 recent 2020s SCOTUS resolved cert petitions (including November 16, 2026 order-list denials and one GVR in `25-1421`, showing typical `distribution_count` values of `1`–`6` and `sal-v8` salience scores).

3. `uv run fedcourts query --court scotus --party "Alvin E. Williams" --limit 20`
   - Transfer line: none (CLI argument error, Exit Code 2: `No such option: --party`).
   - Result: Displayed valid `fedcourts query` flags (`--docket-number`, `--court`, `--era`, `--disposition`, etc.).

4. `uv run fedcourts query --court scotus --docket-number 25-485`
   - Stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned `scotus/73278532` (*Alvin E. Williams, et ux. v. Superior Court of California, Los Angeles County, et al.*), originating from `Court of Appeal of California, Second Appellate District` (`B343233`), `date_filed: "2025-10-20"`, `distributed_for_conference: "2026-01-09"`, `distribution_count: 1`, `disposition: "denied"`, `date_cert_denied: "2026-01-12"`, `salience_score: 0.013`.

5. `uv run fedcourts query --court scotus --docket-number 18-424`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/66649153` (*Judith M. Brown-Williams, et vir v. Superior Court of California, Los Angeles County, et al.*), originating from `Court of Appeal of California, Second Appellate District` (`B289097`), respondents `Bentley Motors, Inc. Rusnak/Pasadena` and `Bradley & Gmelich`, `date_filed: "2018-10-03"`, `distribution_count: 1`, `disposition: "denied"`, `date_cert_denied: "2018-12-03"`.

6. `uv run fedcourts query --court scotus --docket-number 12-26`
   - Stderr: `ranged corpus reads: 745 GET(s), 195297280 byte(s)`
   - Result: Returned `scotus/66504730` (`docket_number: "12-26"`, `date_filed: "2012-07-06"`, `originating_court: "cal"`, sparse bulk-import row).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", q='"B356638"')`
   - Result: `count: 0` (no published or unpublished opinion text indexed on CourtListener for California Court of Appeal docket `B356638`, consistent with a summary writ denial).

2. `mcp_courtlistener_search(type="o", case_name="Alvin E. Williams")`
   - Result: `count: 15` (general name matches in unrelated jurisdictions; none for `B356638`).

3. `mcp_courtlistener_search(type="r", party_name="Alvin E. Williams")`
   - Result: Returned RECAP federal dockets involving Alvin E. Williams (large payload; refined in lookup #5 below with `fields` filter).

4. `mcp_courtlistener_search(type="o", q='"Alvin E. Williams" "Bentley"', fields=["caseName", "court", "court_id", "dateFiled", "docketNumber", "status", "cluster_id"])`
   - Result: `count: 0`.

5. `mcp_courtlistener_search(type="r", q='"Alvin E. Williams" "Bentley"', fields=["caseName", "court", "court_id", "dateFiled", "docketNumber", "dateTerminated", "docket_id"])`
   - Result: `count: 4` federal district court actions in C.D. California (`cacd`):
     - `2:16-mc-00099` (*Alvin E. Williams v. Bentley Morris Inc*, filed 2016-08-10, terminated 2016-08-17)
     - `2:12-cv-05685` (*Alvin E. Williams v. Bentley Motors Inc.'s*, filed 2012-06-29, terminated 2013-07-30)
     - `2:13-cv-07759` (*Alvin E. Williams v. Superior Court of Los Angeles County*, filed 2013-10-21, terminated 2015-06-19)
     - `2:14-cv-07618` (*Judith M. Brown-Williams v. Bentley Motors Inc.*, filed 2014-10-01, terminated 2014-12-17)

## 3. Web Searches and Live Docket Checks

1. `google_web_search(query='"B356638" "Williams" "Superior Court"')`
   - Result: Identified California Court of Appeal (Second Appellate District) Case No. `B356638` and California Supreme Court Case No. `S298340` as *Williams v. Superior Court (Bentley Motors, Inc.)*, petition for review denied October 21, 2026, arising out of Los Angeles Superior Court Case No. `BC342574` (a 2004 Song-Beverly Act "lemon law" suit over a 2004 Bentley Arnage in which petitioners were later declared vexatious litigants).

2. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-646.html`
   - Result: Confirmed live docket matches provisioned snapshot `2026-11-18.json` (docketed Nov. 17, 2026; petition filed Nov. 9, 2026; response due Dec. 17, 2026; no respondent counsel entered; no PDF URLs posted for the pro se paper filing). Personal contact details on the public docket were disregarded and withheld per pipeline privacy rules.

3. `google_web_search(query='"Alvin E. Williams" "Bentley Motors" OR "S298340"')`
   - Result: Returned no results.

4. `google_web_search(query='site:supremecourt.gov "Alvin E. Williams"')`
   - Result: Identified Petitioners' three prior U.S. Supreme Court certiorari petitions in the same dispute: `No. 25-485` (docketed Oct. 20, 2025; denied Jan. 12, 2026), `No. 18-424` (denied Dec. 3, 2018), and `No. 12-26` (denied Oct. 1, 2012).

5. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/25-485.html`
   - Result: Confirmed `No. 25-485` (*Alvin E. Williams, et ux. v. Superior Court of California, Los Angeles County, et al.*, lower court `B343233`) had no response or waiver filed, was distributed once on Dec. 3, 2025 for the Jan. 9, 2026 conference, and was denied on Jan. 12, 2026.

6. `google_web_search(query='"B356638" OR "B343233" "Williams"')`
   - Result: Confirmed continuity between `B343233` (`SCOTUS No. 25-485`) and `B356638` / `S298340` (`SCOTUS No. 26-646`) as successive appellate writ proceedings in the post-2007-verdict *Williams v. Bentley Motors* litigation.

7. `google_web_search(query='"25-485" "Alvin E. Williams" "Questions Presented" OR "certiorari"')`
   - Result: Summarized the five questions presented in `No. 25-485` from `supremecourt.gov` (judicial immunity in cases of alleged judicial fraud, obstruction of entry of final judgment after a 2007 jury verdict, refusal to reach fraud claims on procedural grounds under the Fourteenth Amendment Due Process Clause, and *Hazel-Atlas Glass Co. v. Hartford-Empire Co.*, 322 U.S. 238 (1944)). No forecasts or odds for `No. 26-646` (or `No. 25-485`) surfaced.
