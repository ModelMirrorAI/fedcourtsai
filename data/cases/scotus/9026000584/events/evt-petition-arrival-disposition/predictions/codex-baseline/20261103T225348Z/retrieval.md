# Retrieval record

## Provisioned and repository material

Read the prediction prompt and applicable output schemas; the event definition; the snapshot `2026-11-04.json`; `context.json`; `documents.json`; questions presented; petition; relevant portions of the appendix and matching decision below; lower-court docket summary; and the empty same-question list. Consulted `metrics/statpack.md` for modern-cert, circuit, relist, CVSG, amicus and sal-v6 prior-Term state-band context. Inspected the top-level keys of `metrics/statpack.json`; no additional rate from that inspection was used. Repository file discovery listed paths, not outcome contents. No realized outcome file, other cell output, or QP-topic artifact was read.

## Local tooling attempts

- `uv run fedcourts paths --court scotus --docket 9026000584 --event evt-petition-arrival-disposition --role predictor` failed because the default uv cache was read-only. It returned no case evidence.
- Reissued as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000584 --event evt-petition-arrival-disposition --role predictor`; it returned the case, corpus and event paths, and identified outcomes as evaluator-only.
- Read `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help`, then its opening section with `COLUMNS=140`, to check supported structured filters. These were help requests, not corpus reads.

## Corpus queries

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '576 U.S. 200' --decided-before 2026 --limit 3`

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

   No match. The tool warned that only 200 scoped rows carry reporter citations and that this column matches a case's own citation, not citations to an authority. I treated the result as a coverage gap, not evidence Walker was absent, and switched to CourtListener.

2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2010s --disposition granted --decided-before 2026 --limit 3`

   `ranged corpus reads: 229 GET(s), 59637760 byte(s)`

   Returned *Johnson v. Arteaga-Martinez* (19-896, distribution count 3), *Hughes v. Northwestern University* (19-1401, count 3 and a CVSG), and *Dobbs v. Jackson Women's Health Organization* (19-1392, count 22). These are substantively unrelated and were only procedural illustrations. Grant filtering makes them unsuitable for estimating grant probability. No opinion bodies were requested. The unexpectedly large read volume is recorded rather than represented as just the three returned rows.

3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 25-107 --decided-before 2026 --limit 1`

   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`

   Returned *Leah Gilliam v. David Gerregano*, case `scotus/73274790`, a separate petition denied December 8, 2025, with two distributions and no CVSG. Used as prior history of this legal question, not as an outcome of the case being predicted.

No replay clock was exported; all three lookups nevertheless used a 2026 strictly prior-Term clock. All were metadata-only queries.

## CourtListener MCP

1. Opinion search, citation `576 U.S. 200`, limit 1, fields case name/date/citations/URL/opinions. Returned Walker, opinion 2809762, dated June 18, 2015. Citation matching reported multiple results; the returned case was the intended one.
2. Opinion search, case name `Gilliam v. Gerregano`, court `tenn`, limit 2. Returned the Tennessee Supreme Court's February 26, 2025 decision, opinion 10806629, with its official court PDF location.
3. `search_document` on opinions `[10806629, 2809762]`, literal `personalized`, context 650 characters. Confirmed Gilliam's government-speech holding and Walker's exclusion of the personalization program from its issue. The service displayed up to twenty Gilliam excerpts and one Walker excerpt; no full opinion was requested.
4. Opinion search, citation `148 A.3d 319`, limit 1. Returned an unrelated New York workers' compensation case, *Claim of Pendock v. Matrix Communications Group*. Discarded as a fuzzy citation mismatch; no substantive reliance.
5. Corrected opinion search, case name `Mitchell`, court `md`, dates January 1–December 31, 2016, limit 2. Returned the intended *Mitchell v. Maryland Motor Vehicle Administration*, 148 A.3d 319, opinion 4093604, dated October 28, 2016.
6. `search_document` on opinion 4093604, literal `private speech`, context 250 characters. Confirmed both the private-speech classification and Maryland's holding that its restriction was reasonable and viewpoint-neutral in a nonpublic forum. Used to evaluate Virginia's ability to win on remand even if the classification remains intact.

No live CourtListener query concerned the predicted Supreme Court petition or its subsequent history. No direct REST fallback was used.

## Web attempts

These calls supplied no usable additional evidence in the returned tool messages; the forecast rests on the provisioned record, statpack, corpus and CourtListener material above. Record of each attempted search/open:

1. Search batch: `site.tncourts.gov Gilliam Gerregano 2025 personalized license plate government speech`; `site.in.gov Vawter 2015 45 N.E.3d 1200 license plate`; `site.courts.state.md.us Mitchell 2016 personalized license plate 148 A.3d 319`.
2. Search batch: `Gilliam Gerregano Tennessee Supreme Court 2025`; `Mitchell Maryland Motor Vehicle Administration 2016 vanity plates`.
3. Attempted opening of `https://www.courts.state.md.us/data/opinions/coa/2016/50a15.pdf`. This did not supply verified Mitchell material; discarded and subsequently replaced with the corrected CourtListener search.
4. Attempted opening of the official Gilliam court PDF location returned by CourtListener: `https://www.tncourts.gov/sites/default/files/OpinionsPDFVersion/Majority%20Opinion%20-%20M2022-00083-SC-R11-CV.pdf`. No additional readable evidence was used beyond the MCP excerpts.
5. Attempted opening of the separate, historical Gilliam Supreme Court docket: `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-107.html`. No usable additional evidence; its prior denial was instead obtained through the corpus lookup above.

No web query sought Jack v. Whateley's disposition or later history. No outcome-revealing material about that petition was encountered.
