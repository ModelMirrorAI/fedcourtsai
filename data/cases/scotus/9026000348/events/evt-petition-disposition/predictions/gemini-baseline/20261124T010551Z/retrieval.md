# Retrieval Log — `scotus/9026000348` (`evt-petition-disposition`, run `20261124T010551Z`)

Mode: `forward` (`decided_before: null`). No outcome or third-party/published forecast of this case was sought or encountered.

## 1. `fedcourts` CLI Lookups

1. `uv run fedcourts paths --court "scotus" --docket "9026000348" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Resolved local paths and printed CLI flag documentation (no corpus reads).
2. `uv run fedcourts query --court scotus --disposition gvr --era roberts --limit 10` (chained with two other queries that did not run because this first command exited on flag validation)
   - Failed with usage error: `Unknown era 'roberts'; an era is one decade token — not a court, a Term or a date range.` No ranged corpus reads executed.
3. `uv run fedcourts query --court scotus --docket-number 26-304 --include-open`
   - stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Returned 1 row: `scotus/9026000304`, *United States v. Devonte Devon Jackson, et al.*, docketed `2026-09-08`, `distributed_for_conference: "2026-12-04"`, `distribution_count: 1`, `disposition: null`.
4. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 15`
   - stderr: `ranged corpus reads: 40 GET(s), 10354688 byte(s)`
   - Returned 15 recent SCOTUS GVR priors in the 2020s era (e.g., `25-901`, `25-918`, `26-48`).
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from cached pages in same ranged session / OS cache)
   - Returned 15 recent OT2026 SCOTUS granted priors (including Solicitor General petitions `26-239`, `26-204`, `25-1103`, `25-1343`, and `26-104`, showing typical `distribution_count` of 2 on relisted plenary grants vs. 1 on immediate grants).
6. `uv run fedcourts query --court scotus --citation "580 U.S. 288"`
   - stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)` (plus CLI note that only 195 SCOTUS rows carry reporter citations; returned 0 matching rows).
7. `uv run fedcourts query --court scotus --docket-number 24-1248`
   - stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned 1 row: *United States v. Patrick Darnell Daniels, Jr.*, held SG petition resolved `2026-06-29` as `denied` with `distribution_count: 4`.
8. `uv run fedcourts query --court scotus --docket-number 24-1249`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 1 row: *United States v.Donnell Sam*, held SG petition resolved `2026-06-29` as `denied` with `distribution_count: 4`.
9. `uv run fedcourts query --court scotus --docket-number 18-428`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (in chained shell output after `24-1248`/`24-1249`)
   - Returned 1 row: *United States v. Salas*, held SG petition resolved in June 2019 as `denied` with `distribution_count: 2`.
10. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2025 --limit 15`
    - stderr: `ranged corpus reads: 74 GET(s), 19267584 byte(s)`
    - Returned 15 pre-OT2025 2020s GVR priors (including held petitions such as `24-1097`, `24-1098`, and SG hold petition `23-1341` *NRC v. Fasken Land and Minerals*, showing `distribution_count >= 2` upon post-hold GVR).
11. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 20`
    - stderr: `ranged corpus reads: 10 GET(s), 2490368 byte(s)`
    - Returned 20 recent 2020s denied SCOTUS priors.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca9", case_name="United States v. Jackson", filed_after="2026-01-01", num_results=5)`
   - Returned `count: 0` (caption indexed under full party name or not matched under that string).
2. `mcp_courtlistener_search(type="o", court="ca3", case_name="United States v. Giraud", filed_after="2025-01-01", num_results=5)`
   - Returned `count: 1`: *United States v. Julien Giraud, Jr.*, Nos. 25-2635 & 25-2636 (3d Cir. filed `2025-12-01`, `cluster_id: 10745263`).
3. `mcp_courtlistener_search(type="o", court="ca9", docket_number="25-6214", num_results=5)`
   - Failed with HTTP 429 rate-limit error (`25/min` shared limit).
4. `mcp_courtlistener_search(type="o", court="ca4", docket_number="25-4673", num_results=5)`
   - Failed with HTTP 429 rate-limit error (`25/min` shared limit).
5. `mcp_courtlistener_search(type="o", court="ca4", docket_number="25-4674", num_results=5)`
   - Failed with HTTP 429 rate-limit error (`25/min` shared limit).
6. `mcp_courtlistener_search(type="o", court="ca4", q=""25-4673" OR "25-4674"")`
   - Returned `count: 0` (confirming no published Fourth Circuit opinion in the E.D. Va. FVRA appeals *United States v. James* / *United States v. Comey* had been indexed in CourtListener opinions).
7. `mcp_courtlistener_search(type="o", citation="580 U.S. 288")` (first attempt)
   - Failed with HTTP 429 rate-limit error (`Expected available in 4 seconds`).
8. `mcp_courtlistener_search(type="o", citation="580 U.S. 288")` (retry)
   - Returned `count: 3`, led by *Nat'l Labor Relations Bd. v. SW Gen., Inc.*, 580 U.S. 288 (`dateFiled: "2017-03-21"`, `cluster_id: 4376985`, author Chief Justice Roberts).
9. `mcp_courtlistener_search(type="o", citation="35 F.4th 1328")`
   - Returned `count: 1`: *Arthrex, Inc. v. Smith & Nephew, Inc.*, 35 F.4th 1328 (`court_id: "cafc"`, `dateFiled: "2022-05-27"`, `cluster_id: 6472720`).

## 3. Official `supremecourt.gov` Web Fetches

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-304.html` and `https://www.supremecourt.gov/docket/docketfiles/html/public/26-348.html`
   - Returned static HTML shell metadata and initial docket entries through early/mid-November 2026 (prior to the dynamic JSON distribution entries).
2. `web_fetch` on `https://www.supremecourt.gov/RSS/Cases/JSON/26-304.json` and `https://www.supremecourt.gov/RSS/Cases/JSON/26-348.json`
   - Returned full live official docket JSON for both companion cases as of November 24, 2026, confirming that both *United States v. Jackson* (No. 26-304) and *United States v. Office of the New York State Attorney General* (No. 26-348) had cert replies filed on November 17, 2026, were distributed on November 17, 2026 for the Conference of December 4, 2026 (`distribution_count = 1`), remain undecided, and have zero cert-stage amicus briefs.
3. `web_fetch` on the official filings in companion lead case *United States v. Jackson*, No. 26-304:
   - Brief in Opposition (`https://www.supremecourt.gov/DocketPDF/26/26-304/431502/20261102125312677_261101a%20BIO%20for%20efiling.pdf`)
   - Certiorari Reply Brief (`https://www.supremecourt.gov/DocketPDF/26/26-304/432958/20261117104144524_26-304_Jackson_Cert_Reply.pdf`)
   - Summarized the parties' arguments in *Jackson* regarding collateral-order appellate jurisdiction, mootness / 5 U.S.C. § 3346(a)(2) tolling (and the unconfirmed status of nominee George Kelesis), opposition to consolidating No. 26-348, and the merits of Questions Presented 1 and 2.
