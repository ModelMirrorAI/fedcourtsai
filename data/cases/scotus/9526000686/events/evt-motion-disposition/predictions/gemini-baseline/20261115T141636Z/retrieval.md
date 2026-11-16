# Retrieval Log — `scotus/9526000686` (`evt-motion-disposition`)

Mode: `forward` (`record/context.json`). All retrieval calls attempted beyond the provisioned files in `data/cases/scotus/9526000686/` and the committed `metrics/statpack.md` / `metrics/statpack.json` are listed below.

## 1. Local `fedcourts` CLI Calls

1. `uv run fedcourts query --help`
   - Result: Printed CLI flags and filter documentation (no corpus transfer).
2. `uv run fedcourts paths --court "scotus" --docket "9526000686" --event "evt-motion-disposition" --role predictor`
   - Result: Resolved `case_id` (`scotus/9526000686`), `corpus` (`corpus/corpus.db`), and `event` path; verified `DECIDED_BEFORE` and `REPLAY_CUTOFF` were unset.
3. `uv run fedcourts query --court scotus --docket-number 26-6154`
   - Transfer: `ranged corpus reads: 21 GET(s), 5439488 byte(s)`
   - Result: Returned 1 row (`scotus/9026006154`, *Thomas M. Overton v. Florida, et al.*, `26-6154`, filed `2026-11-14`, `capital_case: true`, originating from the Supreme Court of Florida `SC2026-1724, SC2026-1725`, `disposition: null`).
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned 10 recent denied SCOTUS priors (including substantive applications `26A661` *James Dwight Pavatt v. Oklahoma*, `26A658` *Paul Schultz v. H. Jason Gold*, and `26A657` *Paul Schultz v. Kevin McCarthy*).
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
   - Transfer: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
   - Result: Returned 15 recent granted SCOTUS priors (including substantive applications `26A560` *Mullin v. Friends of the Ruidosa Church*, `26A512` *Scanlan v. Coalition for Open Democracy*, `26A476` *FCC v. Brown*, and `26A428` *Kenneth Nelsen, Warden v. Christa Gail Pike*).
6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 35`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from warm local corpus service cache)
   - Result: Returned 35 recent denied SCOTUS rows, filtered locally to inspect substantive applications (`26A661`, `26A658`, `26A657`).
7. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 100`
   - Transfer: `ranged corpus reads: 19 GET(s), 4915200 byte(s)`
   - Result: Returned 100 recent denied SCOTUS rows, filtered locally for `capital_case: true` (`26-6095`, `26A661`, `25-7555`, `26-5343`).
8. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 100`
   - Transfer: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   - Result: Returned 100 recent granted SCOTUS rows, filtered locally for `capital_case: true` (`26A428` *Nelsen v. Pike*, `25-1003` *Guerrero v. Johnson*, `25A1235` *Guerrero v. Busby*, `24-7351` *Pitchford v. Cain*).
9. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 500`
   - Transfer: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned 500 recent denied SCOTUS rows, yielding 31 denied substantive applications including 4 recent capital stay applications (`26A661` *James Dwight Pavatt v. Oklahoma*, `26A623` *Jesse Guardado v. Florida*, `26A634` *Jesse Guardado v. Richard Comerford*, and `26A524` *William Reaves v. Florida, et al.*), all 4 with `response_requested: false`, `referred_to_court: true`, and `amicus_briefs: 0`.
10. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 2500`
    - Transfer: None (validation error from corpus service: `limit` must be `<= 500`).
11. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 1000`
    - Transfer: None (validation error from corpus service: `limit` must be `<= 500`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Overton v. State"`, `court=["fla", "ca11"]`, `order_by="dateFiled desc"`, `num_results=10`)
   - Result: `0` hits (`query_id: ea756f9c`).
2. `mcp_courtlistener_search` (`type="o"`, `q=""Thomas Mitchell Overton" OR ("Thomas M. Overton" AND Florida)"`, `court=["fla", "ca11", "flsd"]`, `order_by="dateFiled desc"`, `num_results=15`)
   - Result: `1` hit (`query_id: aa3e00b4`): *Overton v. Jones*, 155 F. Supp. 3d 1253 (S.D. Fla. Jan. 12, 2016) (federal habeas denial).
3. `mcp_courtlistener_search` (`type="o"`, `q=""Woodard" AND "clemency" AND "stay of execution""`, `court=["fla", "scotus"]`, `filed_after="2024-01-01"`, `order_by="dateFiled desc"`, `num_results=15`)
   - Result: `0` hits (`query_id: c52af081`).
4. `mcp_courtlistener_search` (`type="o"`, `q=""Guardado" OR "Hunt v. State" AND "clemency""`, `court=["fla", "scotus"]`, `filed_after="2025-01-01"`, `order_by="dateFiled desc"`, `num_results=10`)
   - Result: `0` hits (`query_id: d26bca51`).
5. `mcp_courtlistener_analyze_citations` (verified 11 citations referenced in reasoning/forecast)
   - Result (`job_id: 88e6d17b`): Verified 9 of 11 citations in CourtListener (*Barefoot v. Estelle*, 463 U.S. 880; *Ohio Adult Parole Authority v. Woodard*, 523 U.S. 272; *Connecticut Board of Pardons v. Dumschat*, 452 U.S. 458; *Herrera v. Collins*, 506 U.S. 390; *Coleman v. Thompson*, 501 U.S. 722; *Ford v. Wainwright*, 477 U.S. 399; *Wainwright v. Booker*, 473 U.S. 935; *Overton v. State*, 801 So. 2d 877; *Overton v. Jones*, 155 F. Supp. 3d 1253); recent Florida `So. 3d` citations (*Sweet v. State*, 293 So. 3d 448; *Hunt v. State*, 428 So. 3d 43) not indexed in CourtListener's reporter table, verified directly from the Florida Supreme Court slip opinion in the `26-6154` Appendix.

## 3. Web Fetches (`supremecourt.gov` Official Docket and Filing Pages Only)

1. `web_fetch` on `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26a686.html` and `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-6154.html`
   - Result: Confirmed live docket state as of November 15, 2026 (both pending with only November 14, 2026 initial entries; extracted PDF links for the certiorari petition and appendix in `26-6154`).
2. `web_fetch` on `https://www.supremecourt.gov/DocketPDF/26/26-6154/432768/20261114143745775_Overton%20Cert%20Petition%20-%20final.pdf` and `https://www.supremecourt.gov/DocketPDF/26/26-6154/432768/20261114143854313_Appendix%20to%20the%20Petition%20for%20Writ%20of%20Certiorari.pdf`
   - Result: Extracted the two Questions Presented, procedural history (1991 MacIvor double murder, 1999 conviction, October 21, 2026 death warrant for November 19, 2026 at 6:00 p.m.), and the unanimous (7–0) November 13, 2026 Supreme Court of Florida decision below (`SC2026-1724` & `SC2026-1725`).
3. `web_fetch` on `https://www.supremecourt.gov/DocketPDF/26/26-6154/432768/20261114143854313_Appendix%20to%20the%20Petition%20for%20Writ%20of%20Certiorari.pdf`
   - Result: Extracted specific state procedural bars (Fla. R. Crim. P. 3.851(d)(1) timeliness, 3.851(e)(2) successiveness, appellate forfeiture, non-cognizability of freestanding actual innocence) and cited Florida precedents (*Guardado v. State*, No. SC2026-1605; *Hunt v. State*, 428 So. 3d 43; *Sweet v. State*, 293 So. 3d 448).
4. `web_fetch` on `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26a623.html` and `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26a524.html`
   - Result: Extracted verbatim docket entries for two recent Florida execution-warrant stay applications submitted to Justice Thomas (*Jesse Guardado v. Florida* and *William Reaves v. Florida, et al.*), confirming that in both cases Florida filed its response without a docketed `Response requested` entry, Justice Thomas referred the application to the full Court, and the Court denied the stay and certiorari with no dissents or separate statements noted.
