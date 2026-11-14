# Retrieval Log — `scotus/9026000088` (`evt-order-call-for-response-disposition`)

Mode: `forward` (unrestricted retrieval; no queries were made for `26-88`'s post-cutoff disposition or any third-party forecasts).

## 1. CLI Path & Corpus Lookups (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000088" --event "evt-order-call-for-response-disposition" --role predictor` and `uv run fedcourts query --help` (followed by `COLUMNS=120 uv run fedcourts query --help | grep -E "^\s*│\s*--"`):
   - Resolved `case_id = scotus/9026000088`, `corpus = corpus/corpus.db`, `event = data/cases/scotus/9026000088/events/evt-order-call-for-response-disposition/event.yaml`, confirmed `DECIDED_BEFORE` unset, and listed structured query flags.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
   - Stderr transfer: `ranged corpus reads: 42 GET(s), 10944512 byte(s)`
   - Result: Returned 15 resolved 2020s SCOTUS granted rows (recent OT2025/OT2026 cert grants and interim applications) for baseline schema and signal comparison.
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 15`
   - Stderr transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   - Result: Returned 15 resolved 2020s SCOTUS denied rows.
4. `uv run fedcourts query --court scotus --judge "Owen Dennis Yeates" --limit 20`
   - Stderr transfer: `ranged corpus reads: 744 GET(s), 194904064 byte(s)`
   - Result: Empty (0 rows; `--judge` indexes judicial panels rather than counsel).
5. `uv run fedcourts query --court scotus --docket-number 25-1248`
   - Stderr transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned `scotus/73292884`, *Rio Grande Foundation v. Maggie Toulouse Oliver* (`salience_score: 0.0325`, `distribution_count: 2`, `disposition: "denied"`, `date_cert_denied: "2026-10-05"`).
6. `uv run fedcourts query --court scotus --docket-number 23-926`
   - Stderr transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72483395`, *No on E, San Franciscans Opposing the Affordable Housing Production Act, et al. v. David Chiu, et al.* (`counsel: Alan Gura`, `distribution_count: 2`, `disposition: "denied"`, `date_cert_denied: "2024-10-07"`).
7. `uv run fedcourts query --court scotus --docket-number 23-1251`
   - Stderr transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72479559`, *Paula Bourne, et vir v. Banner University Medical Center Phoenix, LLC* (unrelated petition checked after a web-search summary misstated *Smith v. Stillie*'s docket number; disregarded).
8. `uv run fedcourts query --court scotus --docket-number 21-890`
   - Stderr transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72475052`, *Gaspee Project, et al. v. Diane C. Mederos, et al.* (`distribution_count: 3`, `disposition: "denied"`, `date_cert_denied: "2022-04-25"`).
9. `uv run fedcourts query --court scotus --docket-number 26A349`
   - Stderr transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   - Result: Returned `scotus/9526000349`, *Americans for Prosperity Foundation, et al. v. Anthony Albence, et al.* (`response_requested: true`, `referred_to_court: true`, `disposition: "denied"`, `date_decided: "2026-10-01"`).
10. `uv run fedcourts query --court scotus --docket-number 23-1316`
    - Stderr transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Result: Returned `scotus/72479625`, *Doug Smith, et al. v. Richard Stillie, Jr., in His Official Capacity as Chair, Alaska Public Offices Commission, et al.* (`distribution_count: 6`, `disposition: "denied"`, `date_cert_denied: "2024-11-18"`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Alaska Policy Forum v. Alaska Public Offices Commission", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions", "judge"], num_results=5)`
   - Result: 1 match — *Alaska Policy Forum v. Alaska Public Offices Commission; Yes on 2 for Better Elections; and Protect My Ballot*, `583 P.3d 701`, No. S-18533 (`court_id: "alaska"`, `dateFiled: "2026-02-13"`, `cluster_id: 10793865`, `opinion_id: 11260453`, `judge: "Dario Borghesan"`).
2. `mcp_courtlistener_search(type="o", q='"No on E" Chiu OR "Smith v. Helzer" OR "Gaspee Project" Mederos')`
   - Result: 8 matches including *No on E v. Chiu* (`opinion_id: 9893329`, 85 F.4th 493 (9th Cir. 2023)), *Smith v. Helzer* (`opinion_id: 9951124`, 95 F.4th 1207 (9th Cir. 2024)), *Rio Grande Foundation v. Oliver* (`opinion_id: 11135093`, 154 F.4th 1213 (10th Cir. 2025)), *Center for Arizona Policy Inc. v. Arizona Secretary of State* (`opinion_id: 11349278` (Ariz. June 29, 2026)), and *Americans for Prosperity v. Meyer* (`opinion_id: 11456510` (9th Cir. Sept. 30, 2026)).
3. `mcp_courtlistener_read_document(opinion_id=11260453, chunk_index=[3,4,5,6,7,8,9,10,11,12], chunk_size=8000)`
   - Result: Error — `"No text is available for this document."`
4. `mcp_courtlistener_search(type="o", court="scotus", q='"No on E" OR "Gaspee Project" OR "Helzer" OR "Rio Grande Foundation" OR "Wyoming Gun Owners"')`
   - Result: 16 results; confirmed no published Supreme Court opinions or dissents from denial in *No on E v. Chiu*, *Gaspee Project v. Mederos*, *Smith v. Stillie*, or *Rio Grande Foundation v. Oliver*.
5. `mcp_courtlistener_read_document(opinion_id=11456510, chunk_index=[0,1], chunk_size=8000)`
   - Result: Error — `"No text is available for this document."`
6. `mcp_courtlistener_read_document(opinion_id=9951124, chunk_index=[0,1], chunk_size=8000)`
   - Result: Read opening chunks (`total_chars: 133918`) of *Smith v. Helzer*, 95 F.4th 1207 (9th Cir. 2024), reviewing Alaska's Ballot Measure 2 donor-reporting and on-communication top-three-donor disclaimer provisions.
7. `mcp_courtlistener_read_document(opinion_id=9893329, chunk_index=[0,1], chunk_size=8000)`
   - Result: Read opening chunks (`total_chars: 157728`) of *No on E v. Chiu*, 85 F.4th 493 (9th Cir. 2023), reviewing San Francisco's on-communication donor-disclaimer ordinance and en banc dissents.
8. `mcp_courtlistener_read_document(opinion_id=11135093, chunk_index=[0,1], chunk_size=8000)` and `mcp_courtlistener_read_document(opinion_id=11135093, chunk_index=[11,12], chunk_size=8000)`
   - Result: Read majority opening and Judge Eid's dissenting opinion (`total_chars: 102908`) in *Rio Grande Foundation v. Oliver*, 154 F.4th 1213 (10th Cir. 2025), addressing 501(c)(3) issue advocacy and donor earmarking under *AFPF v. Bonta*.

## 3. Web Searches & Web Fetches

1. `google_web_search(query='"No on E" "Chiu" certiorari OR "Smith v. Helzer" certiorari OR "Gaspee Project" certiorari')`
   - Result: Identified cert denials in *No on E v. Chiu* (No. 23-926, Oct. 7, 2024), *Gaspee Project v. Mederos* (No. 21-890, Apr. 25, 2022), and *Smith v. Stillie* (Nov. 18, 2024; search summary misstated docket number as 23-1251, verified below).
2. `google_web_search(query='"Rio Grande Foundation v. Oliver" certiorari OR "Wyoming Gun Owners" certiorari')`
   - Result: Identified *Rio Grande Foundation v. Oliver*, No. 25-1248 (cert. denied Oct. 5, 2026) and noted no cert petition was filed in *Wyoming Gun Owners v. Gray*.
3. `google_web_search(query='"583 P.3d 701" "Alaska Policy Forum"')`
   - Result: Returned summaries of *Alaska Policy Forum v. Alaska Public Offices Commission*, 583 P.3d 701 (Alaska Feb. 13, 2026).
4. `web_fetch` on `https://caselaw.findlaw.com/court/ak-supreme-court/118218993.html` and its search-grounding redirect URL:
   - Result: Failed (`403 Forbidden` on both URLs).
5. `google_web_search(query='"583 P.3d 701" ("Borghesan" OR "dissent" OR "concurring" OR "Furgatch" OR "earmarking")')`
   - Result: Confirmed Justice Borghesan's February 13, 2026 Alaska Supreme Court opinion was unanimous (5–0; Chief Justice Maassen and Justices Carney, Borghesan, Henderson, and Pate) with no dissents or separate concurrences.
6. `google_web_search(query='"Albence" "Americans for Prosperity" certiorari OR "25-1248" "Rio Grande Foundation"')`
   - Result: Returned procedural details on *Rio Grande Foundation v. Oliver* (No. 25-1248, cert. denied Oct. 5, 2026) and *Americans for Prosperity Foundation v. Albence* (No. 26A349, emergency injunction denied Oct. 1, 2026).
7. `google_web_search(query='"Smith v. Stillie" site:supremecourt.gov')`
   - Result: Confirmed *Smith v. Stillie*, 145 S. Ct. 567 (Nov. 18, 2024), cert denial on Alaska's Ballot Measure 2 disclosure/disclaimer provisions.
8. `google_web_search(query='"No on E" "23-926" "Response requested" OR "25-1248" "Response requested" site:supremecourt.gov')`
   - Result: Confirmed `supremecourt.gov` docket entries showing the Court called for a response after respondent waivers in both *No on E* (No. 23-926, Apr. 9, 2024) and *Rio Grande Foundation* (No. 25-1248, May 26, 2026) prior to denying certiorari.
9. `google_web_search(query='"Smith v. Stillie" "145 S. Ct. 567" "No."')`
   - Result: Confirmed *Smith v. Stillie*'s Supreme Court docket number (`23-1316`), then verified via `fedcourts query` above.
