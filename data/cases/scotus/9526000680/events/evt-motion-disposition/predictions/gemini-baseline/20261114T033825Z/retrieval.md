# Retrieval Log

## 1. Corpus CLI Queries (`fedcourts`)

- `uv run fedcourts paths --court "scotus" --docket "9526000680" --event "evt-motion-disposition" --role predictor`
  - Resolved `case_id` (`scotus/9526000680`), corpus path, and `event.yaml` path (no corpus transfer line).
- `uv run fedcourts query --help`
  - Inspected structured filter flags (no corpus transfer line).
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Returned 10 recent 2020s SCOTUS denied dockets (including substantive stay denials `26A661`, `26A658`, and `26A657`).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache in combined command with prior query; second invocation below reported full ranged reads)
  - Returned 10 recent 2020s SCOTUS granted dockets (including substantive stay grants `26A560`, `26A512`, and `26A476`).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 50`
  - `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
  - Returned 50 recent 2020s SCOTUS grants; filtered to `"application_kind":"substantive"` (17 substantive interim grants, all represented sovereign/institutional/organizational applicants with `referred_to_court: true`).
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 50`
  - `ranged corpus reads: 2 GET(s), 524288 byte(s)`
  - Returned 50 recent 2020s SCOTUS denials; filtered to `"application_kind":"substantive"` (`26A661`, `26A658`, `26A657`).

## 2. CourtListener MCP Calls

- `mcp_courtlistener_search` (`type="r"`, `court=["ca2", "ctd"]`, `party_name="Dowden"`)
  - Returned 1 match: *Dowden v. Deutsche Bank National Trust Company*, No. 3:26-cv-01038 (`ctd`, `docket_id: 73553254`, filed `2026-06-30`).
- `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Malliotakis v. Williams"`)
  - Returned 0 opinion matches under exact `case_name` filter.
- `mcp_courtlistener_search` (`type="rd"`, `docket_number="3:26-cv-01038"`, `document_number=133`)
  - Returned 1 RECAP entry (`ECF No. 133`, Nov. 9, 2026 order denying TRO/preliminary injunction, `is_available: false`).
- `mcp_courtlistener_search` (`type="rd"`, `court="ctd"`, `docket_number="3:26-cv-01038"`, `order_by="entry_date_filed desc"`)
  - Returned recent docket filings in `3:26-cv-01038`, identifying `ECF No. 134` (`id: 500741577`, Nov. 9, 2026 Amended Ruling and Order denying TRO/preliminary injunction, `is_available: true`).
- `mcp_courtlistener_read_document` (`recap_document_id=500741577`)
  - Read the full 29-page (65,546-character) Amended Ruling and Order by U.S. District Judge Sarala V. Nagala in *Dowden v. Deutsche Bank National Trust Co.*, No. 3:26-cv-01038 (SVN), ECF No. 134 (D. Conn. Nov. 9, 2026), detailing the state Superior Court and Connecticut appellate procedural history and the automatic stay rule under Connecticut foreclosure practice.
- `mcp_courtlistener_search` (`type="o"`, `case_name="Dowden v. Deutsche Bank"`)
  - Returned 0 published state appellate opinions (confirming Applicant's statement that the Connecticut appellate orders were unpublished summary orders).
- `mcp_courtlistener_analyze_citations`
  - Verified 9 of 9 case citations: *Hollingsworth v. Perry*, 558 U.S. 183 (2010); *Cox Broadcasting Corp. v. Cohn*, 420 U.S. 469 (1975); *National Socialist Party of America v. Skokie*, 432 U.S. 43 (1977); *Flynt v. Ohio*, 451 U.S. 619 (1981); *Johnson v. Fankell*, 520 U.S. 911 (1997); *Tennessee v. Lane*, 541 U.S. 509 (2004); *United States v. Georgia*, 546 U.S. 151 (2006); *Essex Savings Bank v. Frimberger*, 26 Conn. App. 80 (1991); and *Peralta v. Heights Medical Center, Inc.*, 485 U.S. 80 (1988).
- `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Malliotakis""`)
  - Returned 1 opinion referencing *Malliotakis* (*Allen v. Milligan*, No. 25A1314, June 2, 2026).
- `mcp_courtlistener_search` (`type="r"`, `court="ca2"`, `docket_number="26-3169"`)
  - Returned 0 RECAP dockets for Second Circuit No. 26-3169.

## 3. Web Search Calls

- `google_web_search` (`query=""Malliotakis v. Williams" "25A914""`)
  - Verified the posture and holding of *Malliotakis v. Williams*, No. 25A914 (U.S. Mar. 2, 2026) (6–3 stay of a New York state-court mandatory congressional redistricting injunction ahead of the 2026 midterm election cycle, with Justice Alito concurring and Justice Sotomayor dissenting), cited on page 12 of `application.txt`.
