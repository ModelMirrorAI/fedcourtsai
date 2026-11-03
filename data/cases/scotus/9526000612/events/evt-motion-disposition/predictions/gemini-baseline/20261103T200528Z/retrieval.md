# Retrieval Log

## 1. Corpus Lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26A612`
   - Stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Returned the open corpus record for `scotus/9526000612` (`26A612`, *Martin Akerman v. Merit Systems Protection Board, et al.*, `application_kind: "substantive"`, `originating_court: "cadc"`, `originating_docket_number: "26-5131"`, `disposition: null`).

2. `uv run fedcourts query --court scotus --disposition denied --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recently denied SCOTUS cases (including substantive applications `26A606`, `26A613`, `26A617`, `26A618`, `26A499`, `26A535`, `26A532`, `26A555`, `26A556`, `26A416`).

3. `uv run fedcourts query --court scotus --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Returned 10 recently granted SCOTUS cases (including substantive applications `26A512` and `26A476`, both of which were referred to the full Court and had responses filed, plus cert grants).

4. `uv run fedcourts query --court scotus --include-applications --include-open --limit 50`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 50 recent OT2026 SCOTUS applications (both extension and substantive).

5. `uv run fedcourts query --court scotus --include-applications --disposition denied --limit 30`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 30 recently denied SCOTUS applications and petitions (including `26A536` from CADC, `26A530`, `26A524`, `26A545`, `26A555`, `26A556`, `26A606`, `26A613`, `26A617`, `26A618`).

6. `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 30`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 30 recently granted SCOTUS applications (predominantly time-extension applications).

7. `uv run fedcourts query --court scotus --docket-number 24-339 --full`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/72484053` (*Martin Akerman v. Merit Systems Protection Board, et al.*, No. `24-339`, originating from D.C. Cir. No. `23-5309`, cert denied `2024-11-18`).

8. `uv run fedcourts query --court scotus --docket-number 24-83 --full`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/72487099` (*Martin Akerman v. National Guard Bureau*, No. `24-83`, originating from D.C. Cir. No. `23-1268`, cert denied `2024-10-07`).

9. `uv run fedcourts query --court scotus --docket-number 24-443 --full`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/72484153` (*In Re Martin Akerman*, No. `24-443`, denied `2024-12-16`).

10. `uv run fedcourts query --court scotus --docket-number 24-514 --full`
    - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned `scotus/72484370` (*In Re Martin Akerman*, No. `24-514`, denied `2024-12-16`).

11. `uv run fedcourts query --court scotus --docket-number 24-567 --full`
    - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned `scotus/72484956` (*In Re Martin Akerman*, No. `24-567`, denied `2025-01-27`).

12. `uv run fedcourts query --court scotus --docket-number 23-1106 --full`
    - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned `scotus/72479405` (*Martin Akerman v. United States*, No. `23-1106`, from CAAF No. `24-0060/AF`, cert denied `2024-05-13`).

13. `uv run fedcourts query --court scotus --docket-number 23-623 --full`
    - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned `scotus/72481441` (*Martin Akerman v. Nevada National Guard*, No. `23-623`, from Supreme Court of Nevada No. `86458`, cert denied `2024-02-20`).

14. `uv run fedcourts query --court scotus --docket-number 23-6710 --full`
    - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned `scotus/72481976` (*Martin Akerman v. Sherri Doiron*, No. `23-6710`, from D.C. Cir. No. `23-5230`, cert denied `2024-04-15`).

15. `uv run fedcourts query --court scotus --docket-number 24-1257 --full`
    - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned `scotus/72483756` (*Martin Akerman v. District of Columbia, et al.*, No. `24-1257`, from D.C. Court of Appeals No. `24-CV-749`, cert denied `2025-10-06`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="r", case_name="Akerman v. Merit Systems Protection Board")`
   - Returned 1 RECAP docket: `AKERMAN v. MERIT SYSTEMS PROTECTION BOARD`, D.D.C. No. `1:23-cv-02574` (`docket_id: 67786074`, assigned to Judge Randolph Daniel Moss, FOIA cause of action against MSPB, EEOC, Army, DoD OIG, DOL, OSC, and Air Force).

2. `mcp_courtlistener_search(type="o", court="cadc", case_name="Akerman")`
   - Returned 0 published opinions in the D.C. Circuit index.

3. `mcp_courtlistener_search(type="r", party_name="Martin Akerman")`
   - Returned 20 RECAP dockets (out of 56) involving Martin Akerman across federal courts, including D.C. Cir. No. `26-5131` (`docket_id: 73235695`, *Martin Akerman v. MSPB*, filed April 23, 2026), D.C. Cir. No. `23-5309` (`docket_id: 68113097`, *Martin Akerman v. MSPB*), and D.D.C. No. `1:23-cv-02574` (`docket_id: 67786074`).

4. `mcp_courtlistener_search(type="o", q=""Martin Akerman" "Merit Systems Protection Board"")`
   - Returned 3 opinions mentioning Akerman/MSPB in other matters (*Mary Reese v. Department of the Navy*, *State of California v. Donald J. Trump*, *Akerman v. DoD*).

5. `mcp_courtlistener_search(type="r", docket_number="26-5131")`
   - Returned 57 results across courts matching docket number `26-5131` (superseded by the court-filtered query below).

6. `mcp_courtlistener_get_endpoint_schema(endpoint_id="docket-entries")`
   - Retrieved schema for the `docket-entries` REST endpoint.

7. `mcp_courtlistener_search(type="o", court="scotus", q=""Martin Akerman"")`
   - Returned 0 SCOTUS opinion results.

8. `mcp_courtlistener_search(type="r", court="scotus", q=""Martin Akerman"")`
   - Returned 0 SCOTUS RECAP results.

9. `mcp_courtlistener_search(type="rd", court="cadc", docket_number="26-5131")`
   - Returned 7 RECAP document entries on D.C. Cir. No. `26-5131` (`docket_id: 73235695`), including `Per Curiam Order Filed (Special Panel)` on `2026-08-04` and `Per Curiam Order Filed (Special Panel)` on `2026-10-19`.

10. `mcp_courtlistener_search(type="rd", court="dcd", docket_number="1:23-cv-02574", order_by="entry_date_filed desc")`
    - Returned the 20 most recent RECAP documents on D.D.C. No. `1:23-cv-02574` (`docket_id: 67786074`), showing ongoing district court proceedings and the April 2026 interlocutory appeal transmission (`26-5131`).

11. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", num_results=50, query={"docket": 73235695, "fields": ["id", "date_filed", "entry_number", "description"], "order_by": "-date_filed"})`
    - Returned the 7 docket entry headers for D.C. Cir. No. `26-5131`.

12. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", num_results=50, query={"docket": 67786074, "fields": ["id", "date_filed", "entry_number", "description"], "order_by": "-date_filed"})`
    - Returned the 50 most recent docket entries (March–October 2026) in D.D.C. No. `1:23-cv-02574-RDM`, detailing the pending dispositive motions (`Dkt. 84/87`), preliminary injunction filings, and interlocutory appeal notice (`Dkt. 102`, USCA No. `26-5131`).

13. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=...)` for `72484053` (`24-339`), `72479405` (`23-1106`), `72481441` (`23-623`), `72484153` (`24-443`), `72484370` (`24-514`), `72484956` (`24-567`), `72487099` (`24-83`), `72481976` (`23-6710`), and `72483756` (`24-1257`)
    - Retrieved the SCOTUS docket numbers and basic metadata for Martin Akerman's nine prior SCOTUS petitions so they could be queried in the local corpus via `fedcourts query`.

## 3. Web Searches
- None attempted.
