# Retrieval Log (`scotus/9026000257` / `evt-petition-disposition`)

Mode: `forward` (`record/context.json` `mode: "forward"`, `cutoff: null`). No forecasts or odds of this case were sought or encountered.

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "9026000257" --event "evt-petition-disposition" --role predictor` (plus `uv run fedcourts query --help`)
   - Transfer line: none (`paths` / `--help` metadata command; resolved `case_id scotus/9026000257`, `event.yaml` path, and CLI flag reference).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
   - Returned: 10 recent 2020s SCOTUS `granted` priors (including OT2025/OT2026 grants with distribution counts and CVSG markers).
3. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10` (chained in same shell invocation)
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache from prior command in same invocation)
   - Returned: 10 recent 2020s SCOTUS `gvr` priors.
4. `uv run fedcourts query --court scotus --text "Brumley" --limit 10 && uv run fedcourts query --court scotus --originating-court ca5 --era 2020s --disposition granted --limit 10`
   - Result: Failed (`Exit Code: 2` — `No such option: --text`; second chained command did not run). No transfer line emitted.
5. `uv run fedcourts query --court scotus --docket-number 25-1360 --include-open --full && uv run fedcourts open-events --limit 25`
   - Transfer line (`query`): `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Returned (`query`): Open corpus row for companion/conditional Ten Commandments petition *Cade Brumley, Superintendent, Louisiana State Education, et al. v. Darcy Roake, et al.*, No. `25-1360` (`case_id: "scotus/73500261"`, `distributed_for_conference: "2026-12-11"`, `distribution_count: 3`, `salience_version: "sal-v9"`).
   - Chained `open-events --limit 25`: Failed (`Exit Code: 2` — `open-events` did not accept `--limit` in that invocation).
6. `uv run fedcourts query --court scotus --docket-number 26A15 --include-open --include-applications --full`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: Linked extension application `26A15` (`case_id: "scotus/9526000015"`, `application_kind: "extension"`, granted July 7, 2026).
7. `uv run fedcourts query --court scotus --originating-court ca5 --era 2020s --disposition granted --limit 10 && uv run fedcourts query --court scotus --originating-court ca5 --era 2020s --disposition gvr --limit 10`
   - Result: Failed (`Exit Code: 2` — `No such option: --originating-court`). No transfer line emitted.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="ca5", case_name="Nathan v. Alamo Heights", fields=["caseName", "citation", "cluster_id", "dateFiled", "docketNumber", "opinions", "judge"])`
   - Returned: 1 match (`cluster_id: 10846394`, `opinion_id: 11313761`, *Nathan v. Alamo Heights ISD*, No. 25-50695, filed `2026-04-21`).
2. `mcp_courtlistener_search(type="o", case_name="Stinson v. Fayetteville", fields=["caseName", "court_id", "dateFiled", "docketNumber", "cluster_id", "opinions"])`
   - Returned: `0` results (confirming no Eighth Circuit opinion had been published on CourtListener in *Stinson v. Fayetteville School District No. 1*, No. 26-1722, as of November 26, 2026).
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Mirabelli v. Bonta", fields=["caseName", "citation", "cluster_id", "dateFiled", "opinions"])`
   - Returned: 1 match (`cluster_id: 10802600`, `opinion_id: 11269328`, *Mirabelli v. Bonta*, No. 25A810, 607 U.S. ___ (Mar. 2, 2026) (per curiam)).
4. `mcp_courtlistener_search(type="d", court="ca8", case_name="Stinson v. Fayetteville", fields=["caseName", "court_id", "dateFiled", "docketNumber", "docket_id"])`
   - Returned: `0` RECAP appellate docket entries indexed under `ca8`.
5. `mcp_courtlistener_search_document(opinion_id=11313761, query="rendered", snippet_size=400)` and `mcp_courtlistener_search_document(opinion_id=11313761, query="concurring", snippet_size=400)`
   - Returned: `"No text is available for this document."` on both calls (CourtListener stored only the PDF link without extracted HTML/plain text for `opinion_id=11313761`; relied on `record/documents/petition.txt` Appendix C instead).
6. `mcp_courtlistener_read_document(opinion_id=11269328, chunk_index=0, chunk_size=8000)`
   - Returned: First 8,000 characters of *Mirabelli v. Bonta*, 607 U.S. ___ (Mar. 2, 2026) (per curiam) (vacating Ninth Circuit stay of injunction on parental Free Exercise claims following *Mahmoud v. Taylor*).

## 3. Official Docket & Filing Fetches (`web_fetch`) and Factual Election Lookup (`google_web_search`)

1. `web_fetch` on `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-1360.html` and `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1360.html`
   - Returned: Official Supreme Court docket proceedings for *Brumley v. Roake*, No. 25-1360 (May 21, 2026 conditional petition filed; July 6 waiver; July 28 Response Requested; Oct 19 BIO filed; Nov 4 distributed for 12/4/2026 Conference and cert reply filed; Nov 5 rescheduled).
2. `web_fetch` on the two cert-stage Law & Religion Scholars amicus briefs listed on `2026-11-26.json` (`https://www.supremecourt.gov/DocketPDF/26/26-257/425887/20260928165007811_26-257_Religion%20Scholars%20Amicus%20in%20Support%20of%20Cert_FINAL.pdf` and `https://www.supremecourt.gov/DocketPDF/26/26-257/432377/20261110130612934_Nathan%20v.%20Alamo%20Heights%20-%20Law%20and%20Religion%20Scholars%20Amici%20Brief.pdf`)
   - Returned: Summaries of arguments for Storslee/Meiser/Laycock et al. (supporting cert) and Barclay/DeGirolami/Garnett et al. (opposing cert).
3. `web_fetch` on `https://perma.cc/E8TB-NW5C` (the Perma.cc URL cited in Respondents' BIO pp. 3 n.1 & 32 n.10)
   - Result: Unable to access (`perma.cc` blocked automated fetch).
4. `google_web_search(query='"Texas Attorney General" election winner November 2026')`
   - Returned: Factual election result confirming Democrat Nathan Johnson won the November 3, 2026 Texas Attorney General election (52.4% to 45.9% over Mayes Middleton), taking office in January 2027 (matching the BIO's quotation at pp. 3, 32–33). Zero mention of Supreme Court case No. 26-257 or any litigation forecast.
