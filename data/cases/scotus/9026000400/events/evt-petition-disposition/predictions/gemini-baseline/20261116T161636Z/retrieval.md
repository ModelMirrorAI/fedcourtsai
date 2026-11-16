# Retrieval Log (`scotus/9026000400` / `evt-petition-disposition`)

Mode: `forward` (`DECIDED_BEFORE` unset; `context.cutoff` null; snapshot date `2026-11-16`). No third-party forecasts or predictions of this case were sought or encountered.

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 24-304`
   - Stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: 1 row (`scotus/69981163`, *Laboratory Corporation of America Holdings, dba Labcorp v. Luke Davis, et al.*, granted `2025-01-24` after 4 distributions, `cvsg_date: null`, `merits_judgment: "dismissed-as-improvidently-granted"` on `2025-06-05`; same institutional defense amicus lineup).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
   - Stderr: `ranged corpus reads: 39 GET(s), 10158080 byte(s)`
   - Result: 15 rows of recent OT2026 granted petitions and substantive applications (including `25-944` *Robinhood Markets v. Sodha* granted `2026-11-13` and `25-1408` *Goldman Sachs Bank USA v. Brown* granted `2026-11-06`).
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 10 rows of petitions denied on `2026-11-16` from the `2026-11-13` Conference (`25-1238`, `25-1240`, `25-1303`, `25-1324`, `25-7485`, `25-7562`, `26-4`, `26-62`, `26-100`, `26-120`), confirming the `2026-11-13` Conference order list had issued while `26-400` remained pending awaiting the requested response.
4. `uv run fedcourts query --court scotus --judge "Clifton" --limit 10`
   - Stderr: `ranged corpus reads: 744 GET(s), 194904064 byte(s)`
   - Result: 0 rows (SCOTUS rows do not populate lower-court panel judges in `judges`).
5. `uv run fedcourts query --court scotus --judge "Bybee" --limit 10`
   - Stderr: `ranged corpus reads: 743 GET(s), 194641920 byte(s)`
   - Result: 0 rows.
6. `uv run fedcourts query --court scotus --docket-number 25-874`
   - Stderr: `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
   - Result: 1 row (`scotus/73280372`, *Johnson & Johnson Consumer Inc. v. Narguess Noohi*, CA9 consumer labeling class action, `distribution_count: 1`, `cvsg_date: null`, denied `2026-04-20`).
7. `uv run fedcourts query --court scotus --docket-number 24-576`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: 1 row (`scotus/72485054`, *Nutramax Laboratories, Inc. v. Justin Lytle*, CA9 consumer labeling class action, `distribution_count: 1`, `cvsg_date: null`, denied `2025-03-03`).
8. `uv run fedcourts query --court scotus --docket-number 26-244`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 1 row (`scotus/9026000244`, *The Kroger Co., dba Fred Meyer, Inc. v. Elisha Solano*, CA9 `25-536`, filed `2026-08-25`, distributed `2026-09-28`, `distribution_count: 1`, open).
9. `uv run fedcourts query --court scotus --docket-number 26-376`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: 1 row (`scotus/9026000376`, *Bayer HealthCare LLC v. Doniece Drake*, CA9 `24-7158`, filed `2026-09-18`, `distribution_count: 0`, open, 4 defense amici).
10. `uv run fedcourts query --court scotus --docket-number 24-933`
    - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Result: 1 row (`scotus/72487213`, *State Farm Mutual Automobile Insurance Co. v. Faysal A. Jama*, CA9 `22-35449`, counsel of record Theodore J. Boutrous Jr., `distribution_count: 2`, denied `2025-06-16`).
11. `uv run fedcourts query --court scotus --docket-number 26-592`
    - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: 1 row (`scotus/9026000592`, *Wexford Health Sources, Inc. v. Lauren Spurlock*, CA4 `25-2038`, docketed `2026-11-05`, `distribution_count: 0`, open).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Laboratory Corp. of America Holdings v. Davis"`, `num_results=5`)
   - Returned 2 clusters (`10776843` and `10599006`, `605 U.S. 327`, filed `2025-06-05`, opinion ID `11243430`).
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q='"Noohi v. Johnson" OR "Rosenwald v. Kimberly-Clark" OR "Lytle v. Nutramax" OR "Treasurer v. Boeing" OR "Spurlock v. Wexford"'`, `num_results=10`)
   - Returned 1 unrelated historical opinion (*Edelman v. Boeing Air Transport*, 1933).
3. `mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `case_name="Boeing"`, `filed_after="2025-01-01"`, `num_results=5`)
   - Returned 1 cluster (`10933568`, *In re: The Boeing Company*, No. `25-1492`, filed `2026-07-20`).
4. `mcp_courtlistener_read_document` (`opinion_id=11243430`)
   - Read full text (20,185 chars) of *Laboratory Corp. of America Holdings v. Davis*, 605 U.S. 327 (2025): per curiam DIG with solo dissent by Justice Kavanaugh (no other Justice joining).
5. `mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `docket_number="25-1439"`, `num_results=5`)
   - Returned 1 cluster (`10811292`, *Goldman Sachs Bank USA v. Rhea Brown*, filed `2026-03-18`; warning noted `snippet` not in fields).
6. `mcp_courtlistener_search` (`type="o"`, `court="ca9"`, `docket_number="24-1036"`, `num_results=5`)
   - Returned 1 cluster (`10663157`, *Sodha v. Golubowski*, filed `2025-08-29`; warning noted `snippet` not in fields).
7. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2024-10-01"`, `q='"Speerly" OR "Noohi" OR "Lytle" OR "Rosenwald" OR "Spurlock" OR "Clippinger" OR "Davidson v. Kimberly-Clark" OR "Olean Wholesale"'`, `num_results=20`)
   - Returned 2 clusters (both *Laboratory Corp. of America Holdings v. Davis*, `605 U.S. 327`).
8. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10933568`, `fields=["id", "case_name", "date_filed", "syllabus", "opinions"]`)
   - Failed validation (`Invalid fields: ['opinions']. Did you mean: sub_opinions?`).
9. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10811292`, `fields=["id", "case_name", "date_filed", "syllabus", "opinions"]`)
   - Failed validation (`Invalid fields: ['opinions']. Did you mean: sub_opinions?`).
10. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10811292`, `fields=["id", "case_name", "date_filed", "syllabus", "summary", "sub_opinions"]`)
    - Returned cluster metadata for *Goldman Sachs Bank USA v. Rhea Brown* (`sub_opinions: [11278043]`).
11. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10933568`, `fields=["id", "case_name", "date_filed", "syllabus", "summary", "sub_opinions"]`)
    - Returned cluster metadata for *In re: The Boeing Company* (`sub_opinions: [11401129]`).

## 3. Web Fetches and Searches (`supremecourt.gov` Dockets & Questions Presented)

1. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-400.html`, `https://www.supremecourt.gov/qp/25-01408qp.pdf`, and `https://www.supremecourt.gov/qp/25-00944qp.pdf`
   - Confirmed live docket for `26-400` matches `2026-11-16.json` verbatim (last entry: `Oct 28, 2026: Response Requested. (Due November 27, 2026)`), and confirmed `25-1408` and `25-944` involve unrelated questions (FAA/Bankruptcy § 362(k) and Securities Act § 11(a)).
2. `google_web_search`: `"Nutramax Laboratories" OR "Noohi v. Johnson" OR "Rosenwald v. Kimberly-Clark" "certiorari" site:supremecourt.gov`
   - Confirmed *Nutramax v. Lytle* (No. 24-576, denied Mar. 3, 2025), *Johnson & Johnson v. Noohi* (No. 25-874, denied Apr. 20, 2026), and no petition in *Rosenwald*.
3. `google_web_search`: `"Speerly" "General Motors" OR "Spurlock" "Wexford" OR "Boeing" "uninjured class members" "certiorari" site:supremecourt.gov`
   - Identified *Spurlock v. Wexford Health Sources*, 175 F.4th 232 (4th Cir. 2026) (SCOTUS extension `26A224`) and *Boeing*, 182 F.4th 422 (4th Cir. 2026).
4. `google_web_search`: `"Wexford Health Sources" "Spurlock" OR "Boeing" "182 F.4th 422" OR "Clippinger" "State Farm" site:supremecourt.gov`
   - Confirmed *Wexford* extension to Oct. 29, 2026 (`26A224`), *Boeing* reversed certification, and *Clippinger* (173 F.4th 817) cited in pending Rule 23 petitions (*Bayer v. Drake*, *Kroger v. Solano*, *State Farm v. Jama*).
5. `google_web_search`: `"25-1408" "Goldman Sachs" Question Presented site:supremecourt.gov`
   - Confirmed *Goldman Sachs v. Brown* (No. 25-1408) QP concerns Bankruptcy Code § 362(k) arbitration, unrelated to Rule 23.
6. `google_web_search`: `"Wexford Health Sources" "Spurlock" OR "Bayer HealthCare" "Drake" OR "Kroger" "Solano" OR "State Farm" "Jama" "docketfiles" site:supremecourt.gov`
   - Identified docket numbers `26-244` (*Kroger v. Solano*), `26-376` (*Bayer v. Drake*), and `24-933` (*State Farm v. Jama*).
7. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-244.html`, `https://www.supremecourt.gov/docket/docketfiles/html/public/26-376.html`, and `https://www.supremecourt.gov/docket/docketfiles/html/public/26a224.html`
   - Extracted docket entries for `26-244` (CFR issued Sep. 3, 2026), `26-376` (BIO extended to Nov. 18, 2026; 4 defense amici), and `26A224` (extension to Oct. 29, 2026).
8. `google_web_search`: `("26-244" "Solano" "Questions Presented") OR ("26-376" "Drake" "Questions Presented") OR ("Wexford Health Sources" "Spurlock" "Petition for a writ of certiorari") site:supremecourt.gov`
   - Confirmed `26-244`, `26-376`, and *Wexford* all present the Rule 23(b)(3) / Article III uninjured-class-members question.
9. `google_web_search`: `"Wexford Health Sources" "Spurlock" "Petition for a writ of certiorari filed" site:supremecourt.gov`
   - Identified *Wexford Health Sources, Inc. v. Spurlock* cert docket No. `26-592` (filed Oct. 29, 2026 / docketed Nov. 5, 2026).
