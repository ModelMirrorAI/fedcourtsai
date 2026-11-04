# Retrieval Log

## 1. `fedcourts` CLI Commands & Corpus Queries

1. Path resolution and CLI help:
   - Command: `uv run fedcourts paths --court "scotus" --docket "9526000634" --event "evt-motion-disposition" --role predictor && uv run fedcourts query --help`
   - Result: Resolved `case_id` (`scotus/9526000634`), `corpus` (`corpus/corpus.db`), and `event` path; printed `query` options.
2. Lookup of linked cert petition `26-6051` and recent 2020s SCOTUS priors:
   - Command: `uv run fedcourts query --court scotus --docket-number 26-6051 && uv run fedcourts query --court scotus --era 2020s --limit 20`
   - Ranged corpus reads lines:
     - `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
     - `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned open cert petition `scotus/9026006051` (`26-6051`, *Jesse Guardado v. Richard Comerford*, filed 2026-11-03, originating in `ca11` No. `26-14027`) and 20 recent 2020s SCOTUS resolved cases/applications.
3. Lookup of top 100 recent 2020s SCOTUS cases filtered for capital cases:
   - Command: `uv run fedcourts query --court scotus --era 2020s --limit 100`
   - Ranged corpus reads line:
     - `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned 100 resolved 2020s SCOTUS rows, including capital stay application `scotus/9526000524` (`26A524`, *William Reaves v. Florida*, denied 2026-10-20, `referred_to_court: true`, `response_requested: false`, `response_filed_at: "2026-10-19"`).
4. Attempted lookup with `--limit 1000` (refused by validation limit <= 500):
   - Command: `uv run fedcourts query --court scotus --era 2020s --limit 1000`
   - Result: Validation error (`limit: Input should be less than or equal to 500`).
5. Re-issued lookup with `--limit 500` for capital cases and Florida execution applicants:
   - Command: `uv run fedcourts query --court scotus --era 2020s --limit 500`
   - Ranged corpus reads line:
     - `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Result: Returned 500 resolved 2020s SCOTUS rows, including capital stay applications `26A524` (*William Reaves v. Florida*), `26A456`, `26A459`, and `26A470` (*In Re Jamaal Howard* / *Jamaal Howard v. Texas*), all denied after referral to the Court (`referred_to_court: true`, `response_requested: false`).
6. Lookup of adjacent SCOTUS docket numbers (`26A633`, `26A635`, `26-6050`):
   - Command: `uv run fedcourts query --court scotus --docket-number 26A633 && uv run fedcourts query --court scotus --docket-number 26A635 && uv run fedcourts query --court scotus --docket-number 26-6050`
   - Ranged corpus reads lines:
     - `ranged corpus reads: 0 GET(s), 0 byte(s)`
     - `ranged corpus reads: 0 GET(s), 0 byte(s)`
     - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Confirmed adjacent docket numbers belong to unrelated litigants (*Jason P. Brown v. Colorado*, *William Keith Speer v. Texas*, *Robert Keith Woodall v. Laura Plappert*).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="ca11"`, `docket_number="26-14027"`):
   - Result: `count: 0` (the November 2, 2026 Eleventh Circuit order was not yet indexed in CourtListener opinions).
2. `mcp_courtlistener_search` (`type="r"`, `case_name="Guardado v. Comerford"`):
   - Result: `count: 0`.
3. `mcp_courtlistener_search` (`type="o"`, `court=["scotus", "ca11", "fla"]`, `case_name="Guardado"`, `num_results=10`):
   - Result: `count: 7`, including the Florida Supreme Court's October 29, 2026 decision in *Jesse Guardado v. State of Florida*, No. SC2026-1605 (`cluster_id: 11049070`), and prior direct/postconviction decisions (`965 So. 2d 108`, `176 So. 3d 886`, `226 So. 3d 213`, `238 So. 3d 162`).
4. `mcp_courtlistener_search` (`type="o"`, `court=["scotus", "ca11"]`, `q='etomidate "Guardado" OR "Trotter" OR "Heath"'`, `num_results=10`):
   - Result: `count: 2` (*Bobby Joe Long v. Secretary, Department of Corrections*, 924 F.3d 1171 (11th Cir. 2019)).
5. `mcp_courtlistener_call_endpoint` (`endpoint_id="opinions"`, `query={"cluster": 11049070, "fields": ["id", "type", "author_str"]}`):
   - Result: Returned `opinion_id: 11516852` (`type: "010combined"`).
6. `mcp_courtlistener_read_document` (`opinion_id=11516852`, `chunk_index=0`):
   - Result: Read opening chunk of *Jesse Guardado v. State of Florida*, No. SC2026-1605 (Fla. Oct. 29, 2026), affirming denial of successive state postconviction relief and denying a stay of the November 5, 2026 execution.

## 3. Web Fetches (`web_fetch`, Forward Mode)

1. `web_fetch` of live Supreme Court docket JSONs (`https://www.supremecourt.gov/RSS/Cases/JSON/26A634.json` and `https://www.supremecourt.gov/RSS/Cases/JSON/26-6051.json`):
   - Result: Confirmed both dockets remain open/undecided as of November 4, 2026; showed that on November 4, 2026, Respondent Richard Comerford submitted a response to the stay application in `26A634` (`20261104150435181_26A634 Guardado Response to Stay.pdf`) and a brief in opposition in `26-6051` without a formal response-request entry.
2. `web_fetch` of `https://www.supremecourt.gov/DocketPDF/26/26A634/431853/20261104150435181_26A634%20Guardado%20Response%20to%20Stay.pdf` and `https://www.supremecourt.gov/DocketPDF/26/26A634/431750/20261103182842689_Document.pdf`:
   - Result: Summarized the State's opposition arguments and the lower-court orders bound in the appendix (the November 2, 2026 Eleventh Circuit panel opinion by Chief Judge William Pryor, Judge Jill Pryor, and Judge Robert Luck, Judge Jill Pryor's concurrence regarding FDOC's recordkeeping and Wite-Out alterations, and District Judge Marcia Morales Howard's order following the October 22, 2026 evidentiary hearing).
3. Follow-up `web_fetch` on `https://www.supremecourt.gov/DocketPDF/26/26A634/431750/20261103182842689_Document.pdf`:
   - Result: Extracted the exact Eleventh Circuit panel composition, order date (November 2, 2026), District Judge identity (Judge Marcia Morales Howard, No. 3:26-cv-02596-MMH-SJH), and Section II.B's holding that Guardado's appellate stay motion was silent on the second prong of *Glossip* (identifying a feasible, readily implemented alternative method of execution).
