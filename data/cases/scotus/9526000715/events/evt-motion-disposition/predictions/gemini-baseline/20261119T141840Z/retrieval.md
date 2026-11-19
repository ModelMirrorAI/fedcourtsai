# Retrieval Log — `scotus/9526000715` (`evt-motion-disposition`)

Mode: `forward` (`cutoff: 2026-11-17`). Per the contract, no lookup sought the disposition of Application `26A715`.

## 1. `fedcourts` CLI Lookups

1. `uv run fedcourts paths --court "scotus" --docket "9526000715" --event "evt-motion-disposition" --role predictor` and `uv run fedcourts query --help`
   - Confirmed case/event paths, `DECIDED_BEFORE` unset (`forward` mode), and `fedcourts query` options.
2. `uv run fedcourts query --court scotus --docket-number 26-502`
   - Transfer line: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Returned the corpus row for linked certiorari petition *Rachel Beth Odom v. Oklahoma*, No. `26-502` (`case_id: scotus/9026000502`, filed `2026-10-15`, counsel Lindsay Kistler for petitioner Rachel B. Odom and Kathryn E. Gardner for respondent Minor Child E.O.D., originating court Oklahoma Court of Civil Appeals, Third Division, No. `123,076`, `disposition: null` as of `2026-11-18`).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer line: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Returned 5 recent resolved granted SCOTUS rows in the 2020s (including substantive interim grants `26A560` and `26A512`, both federal/state public-law applications with `response_requested: true`, `referred_to_court: true`, `amicus_briefs: 1`).
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent denied SCOTUS rows including unescalated private substantive stay application `26A698` (*Simpkins v. Tennessee*, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `disposition: "denied"`).
5. `uv run fedcourts query --court scotus --era 2020s --include-applications --disposition granted --limit 20`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 20 recent granted rows, confirming that routine zero-signal application grants without requested responses or referrals are `application_kind: "extension"` rows rather than substantive stays.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Odom", filed_after="2024-01-01", num_results=20)`
   - Returned 24 opinions across jurisdictions; none matched *Rachel Beth Odom* or Oklahoma No. `123,076`.
2. `mcp_courtlistener_search(type="o", q=""123,076" OR "123076" Odom Oklahoma")`
   - Returned 1 unrelated 1977 Oklahoma Court of Civil Appeals opinion (*Anderson v. Vian Cemetery Ass'n*, 571 P.2d 880).
3. `mcp_courtlistener_search(type="o", court=["oklacivapp", "okla"], filed_after="2024-01-01", q=""E.O.D." OR "123,076" OR "123076" OR "Kistler" OR "Odom"")`
   - Returned 9 published Oklahoma Supreme Court opinions (none matching No. `123,076`, indicating the March 9, 2026 Division III opinion in *In re E.O.D.* was not published in OSCN's public CourtListener feed).
4. `mcp_courtlistener_search(type="o", court="scotus", q=""Baxter v. Palmigiano" "adverse inference"")`
   - Returned 4 Supreme Court precedents (*Baxter v. Palmigiano*, 425 U.S. 308 (1976); *Mitchell v. United States*, 526 U.S. 314 (1999); *United States v. Robinson*, 485 U.S. 25 (1988); *United States v. Balsys*, 524 U.S. 666 (1998)).

## 3. Web Searches and Fetches

1. `google_web_search(query=""123,076" OR "DF-123076" OR "IN-123076" Oklahoma "Odom" OR "E.O.D."")`
   - Returned summary of *In re E.O.D., Alleged Deprived Child* / *Rachel Beth Odom v. State of Oklahoma* (Okla. Civ. App. Div. III No. `123,076`; Tulsa County Dist. Ct. Nos. `JD-2025-45` and parallel murder case `CF-2025-676`) and the two constitutional questions presented in SCOTUS No. `26-502`.
2. `google_web_search(query=""26-502" "Rachel Beth Odom" Oklahoma supremecourt.gov")`
   - Returned factual background and procedural history of SCOTUS No. `26-502` (petition filed August 28, 2026; docketed October 15, 2026; response due November 16, 2026; Oklahoma Supreme Court cert denial June 1, 2026 with Justice Darby dissenting). Grounding source list included `supremecourt.gov`, `narf.org`, and `scotusgate.com` (no predictions or probabilities appeared in the summary; disclosed in `flags.json`).
3. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-502.html` (two calls: first for overall metadata/entries, second verifying verbatim Proceedings and Orders rows, counsel, and the Petition PDF URL)
   - Confirmed all four docket entries on No. `26-502` (Aug. 28, 2026 motion to file with supplemental appendix under seal [`26M23`] and cert petition with response due Nov. 16, 2026; Sept. 16, 2026 distribution for 10/9/2026 Conference; Oct. 13, 2026 `Motion Granted`), zero amicus filings, and no response filed yet on the public page.
4. `google_web_search(query="site:supremecourt.gov "26-502" "Rachel Beth Odom"")`
   - Confirmed factual summary from indexed `supremecourt.gov` petition text (grounding metadata again included `scotusgate.com` alongside `supremecourt.gov`, with no forecast content).
5. `google_web_search(query="site:okcourtsandmore.org "123,076" OR "E.O.D." OR "Odom"")`
   - Confirmed lower-court dates: June 4, 2025 deprived adjudication by Hon. Kevin Gray in `JD-2025-45`; March 9, 2026 affirmance by Okla. Civ. App. Div. III in No. `123,076`; June 1, 2026 Okla. Sup. Ct. cert denial (Darby, J., dissenting).
6. `web_fetch` on `https://www.supremecourt.gov/DocketPDF/26/26-502/323845/20260828154414341_Odom%20Petition%20for%20Writ%20of%20Certiorari.pdf`
   - **Failed / refused:** Tool reported inability to fetch the binary PDF from `supremecourt.gov/DocketPDF/...` due to technical domain/PDF limitations.
7. `google_web_search(query=""Rachel Beth Odom" "26-502" ("termination" OR "stay" OR "trial" OR "1257" OR "Cox" OR "ICWA" OR "Indian")")`
   - Surfaced indexed details from the `26-502` petition on `supremecourt.gov`: E.O.D. is an enrolled member of the Chickasaw Nation (triggering ICWA), a motion to terminate parental rights remained pending in the trial court, and petitioner relied on *Cox Broadcasting Corp. v. Cohn* (1975) to argue finality under 28 U.S.C. § 1257. (Grounding metadata included `scotusgate.com` with no forecast content.)
8. `google_web_search(query=""Odom" "123,076" ("Baxter" OR "Garrity" OR "Lefkowitz" OR "split" OR "immunity" OR "Santosky") site:supremecourt.gov")`
   - Surfaced indexed details from the `26-502` petition on `supremecourt.gov`: the trial court granted selective immunity limited to "demeanor and affect," and the petition argues a state-court split under *Baxter v. Palmigiano*, *Garrity v. New Jersey*, *Lefkowitz v. Turley*, and *Santosky v. Kramer*. (Grounding metadata included `scotusgate.com` with no forecast content.)
