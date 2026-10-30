# Retrieval Log: *Juan Baltazar, Warden, et al. v. Eva Daley* (`scotus/9026000146`)

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - `ranged corpus reads: 34 GET(s), 8716288 byte(s)`
   - Purpose: Inspect recent OT 2026 granted petitions and SG petitions in the corpus.
2. `uv run fedcourts query --court ca10 --docket-number 24-1191 --include-open`
   - `ranged corpus reads: 42 GET(s), 11010048 byte(s)`
   - Purpose: Retrieve the originating Tenth Circuit case record (`ca10/69734086`, topic `2463 Habeas Corpus- Alien Detainee`, decided `2025-11-03`).
3. `uv run fedcourts query --court scotus --docket-number 25A1403 --include-applications --include-open`
   - `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Purpose: Inspect the linked extension application `25A1403` (`scotus/73500644`).
4. `uv run fedcourts query --court scotus --docket-number 25-1003 --include-open`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Purpose: Check docket number candidate for *Montoya Palacios*.
5. `uv run fedcourts query --court scotus --docket-number 25-1223 --include-open`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Purpose: Retrieve the lead granted merits case on the same question presented, *Kevin Isaac Montoya Palacios v. Vernon Liggins*, No. 25-1223 (`scotus/73253921`, cert granted `2026-06-29`), where Andrew Timothy Tutt is counsel of record for amici "Eva Daley and Adolph Michelin."
6. `uv run fedcourts query --court scotus --docket-number 26-145 --include-open`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Retrieve the companion SG follow-on petition *Warden, Moshannon Valley Correctional Center, et al. v. Adolph Michelin, et al.*, No. 26-145 (`scotus/9026000145`, filed the same day, `2026-07-31`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="ca10", docket_number="24-1191")` — returned HTTP 429 rate-limit error (daily shared quota exceeded).
2. `mcp_courtlistener_search(type="o", case_name="Daley v. Baltazar")` — returned HTTP 429 rate-limit error (daily shared quota exceeded).

## 3. Web Searches (`google_web_search`)

1. `"Baltazar" "Eva Daley" "24-1191" OR "26-146"` (no results)
2. `"Eva Daley" "Baltazar" Tenth Circuit` (no results)
3. `"24-1191" "Tenth Circuit" "November 3, 2025" OR "2025"` — identified *Daley v. Choate* / *Daley v. Ceja*, No. 24-1191, 157 F.4th 1207 (10th Cir. Nov. 3, 2025), holding that 28 U.S.C. § 2241 immigration habeas proceedings are "civil actions" under the Equal Access to Justice Act (EAJA), 28 U.S.C. § 2412(d)(1)(A).
4. `"Eva Daley" "Andrew Timothy Tutt" OR "Trial Lawyers for Justice"` (no results)
5. `"Daley v. Choate" OR "Daley v. Ceja" "Equal Access to Justice Act" "habeas"` — confirmed the Tenth Circuit split (2-1, Tymkovich, J., dissenting) and the circuit split with the Fourth and Fifth Circuits.
6. `"Equal Access to Justice Act" "habeas" "civil action" "Supreme Court" 2025 OR 2026` — identified the granted lead case *Montoya Palacios v. Liggins*.
7. `"26-146" "Baltazar" "Daley" supremecourt.gov` — confirmed the question presented in No. 26-146 and that it is a follow-on petition by the Solicitor General to *Montoya Palacios v. Liggins*.
8. `"Montoya Palacios v. Liggins" docket number` — confirmed Docket No. 25-1223 (cert granted June 29, 2026).
9. `"Daley v. Ceja" OR "Baltazar v. Daley" "Montoya Palacios" OR "hold"` (no results)
10. `"Baltazar" "Daley" "26-146" "Montoya Palacios" OR "25-1223" OR "Sineneng-Smith"` (no results)
11. `"Baltazar, Warden, et al. v. Eva Daley" OR "Baltazar v. Daley" "Question Presented" OR "Petition for a writ of certiorari"` — confirmed the Solicitor General requested the petition be held pending *Montoya Palacios v. Liggins* (No. 25-1223).
12. `"Adolph Michelin" "Supreme Court" OR "Equal Access to Justice Act" 2026` — confirmed the companion Third Circuit EAJA habeas case *Michelin v. Warden, Moshannon Valley Correctional Center* (No. 26-145).
13. `"26-146" "hold" "Palacios" OR "Liggins" "petition for a writ of certiorari"` (no results)
14. `"25-1223" "Montoya Palacios" oral argument date OR merits` — confirmed *Montoya Palacios v. Liggins* was argued on October 7, 2026 and remains pending on the merits.
15. `"26-145" "Michelin" "Response Requested" OR "Conference"` — confirmed the status of companion petition No. 26-145.
