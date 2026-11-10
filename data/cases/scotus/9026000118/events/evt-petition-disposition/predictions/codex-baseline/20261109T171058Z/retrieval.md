# Retrieval record

## Baseline and repository context

Read the prediction prompt and schemas, the event, the November 9 snapshot, context, document manifest, questions presented, selected jurisdictional-statement and appendix passages, and same-question candidates. Read `metrics/statpack.md`, especially modern dispositions, originating circuits, paid-segment relist/CVSG/amicus cuts, and the sal-v8 per-Term risk-set table. The context's frozen high-band anchor, not a recalculated current-Term rate, supplies the numerical starting point. Inspected the repository's `pdf-text` implementation solely to use its existing extractor on an anonymous in-memory descriptor without persisting downloaded files. Checked applicable instruction-file paths and working-tree status; no other cell output or evaluator artifact was read.

All successful shell CLI invocations used `UV_CACHE_DIR=/tmp/uv-cache` and `uv run --no-sync` to avoid the read-only default cache and avoid dependency installation. No packages were installed.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000118 --event evt-petition-disposition --role predictor` failed because the default uv cache was read-only. No retrieval occurred.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000118 --event evt-petition-disposition --role predictor` succeeded and located the event/corpus paths. The evaluator-only path was withheld and was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` supplied structured-filter usage.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition summary-reversal --era modern --limit 3` was refused: `modern` is not a decade-token era. The error supplied the valid vocabulary; no corpus-transfer line was printed.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 3` completed but returned no prior rows. Its stderr transfer report was:

   `ranged corpus reads: 1071 GET(s), 280756224 byte(s)`

   This broad first lookup was expensive despite yielding no rows. No full opinion hydration was requested.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026-07-22 --limit 3` returned Monsanto v. Salas (24-1097), Monsanto v. Johnson (24-1098), and Petersen v. Doe (24-449), all marked GVR with June 30, 2026 grant dates and distribution counts of four, four, and three. No opinion bodies were returned. Stderr reported the voluntarily imposed July 22 date boundary and:

   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`

## Browser attempts

1. One `web.run` search call contained the queries `site.uscode.house.gov 28 USC 1253 three judges injunction appeal` and `site.supremecourt.gov "Louisiana v. Callais" "2026" opinion`. The tool returned no visible results or usable content.
2. One `web.run` open attempted the September 18, 2026 Singleton motion-to-dismiss PDF linked in the provisioned snapshot. It returned no visible document content. A direct retrieval of that exact filing subsequently succeeded as described below.

Neither browser attempt supplied a target disposition or any facts used in the forecast.

## CourtListener MCP calls

1. `search(type="o", citation="146 S. Ct. 1377", court="scotus", num_results=2)` returned no results. This was a lookup of the previously issued interim stay cited in the jurisdictional statement, not the target appellate disposition.
2. `search(type="o", case_name="Louisiana v. Callais", court="scotus", num_results=3)` returned the April 29, 2026 opinion and its May 4 revision, opinion IDs 11317641 and 11320154. This is a different, already-decided case.
3. `search_document(opinion_id=11320154, query="political goals", snippet_size=900)` returned majority passages, including pages 29–30 on alternative maps and partisan controls, alongside separately identified dissent material. The majority text corroborated the controlling framework.
4. `search(type="o", court="scotus", case_name="Allen", filed_after="2026-06-01", filed_before="2026-06-03", num_results=4, fields=["caseName","dateFiled","docketNumber","opinions","absolute_url"])` returned only the June 2, 2026 Allen v. Milligan stay opinion, opinion ID 11336479, lead application 25A1314. The narrow pre-appeal date window avoided retrieving the event being predicted.
5. `read_document(opinion_id=11336479, chunk_index=0, chunk_size=14000)` returned the beginning of the combined stay opinion, including the disposition's application numbers, per curiam reasoning, and the opening of Sotomayor's dissent joined by Kagan and Jackson. The applications predate the target jurisdictional statement.
6. `search_document(opinion_id=11336479, query="likely to succeed", snippet_size=1700)` supplied the majority's explicit assessment of both claims and specific errors, together with a separately labeled dissent passage. Used to distinguish the Court's own interim reasoning from Alabama's later advocacy.

No direct CourtListener REST endpoint, credential extraction, or current target-docket disposition search was used.

## Direct filing retrieval and PDF extraction

These were exact snapshot-linked, dated filings, not docket-page or outcome searches. Each HTTPS request used Python's standard `urllib.request`, a 25-second timeout, and a 20 MB read cap. PDF bytes stayed in an anonymous `os.memfd_create` descriptor. Text was read using the existing `uv run --no-sync fedcourts pdf-text /proc/self/fd/<descriptor> --max-chars 80000` command, except the first motion extraction used an 85,000-character cap. No downloaded PDF or extra text file was persisted.

1. Retrieved the September 18, 2026 **Motion to Dismiss**, snapshot link under `DocketPDF/26/26-118/424782/`, basename `20260918112621309_Singleton Motion to Dismiss Final.pdf`. Extraction succeeded: `pdf-text: 27 page(s), 35751 character(s)`. Read its questions, procedural position, mootness argument, alternative-map discussion, and conclusion; the displayed combined output was truncated by the terminal. It argues election-specific mootness and disputes Alabama's factual presentation. It does not state the future disposition of this appeal.
2. Retrieved the September 29, 2026 **Response in Opposition to Motion to Dismiss**, snapshot link under `DocketPDF/26/26-118/425967/`, basename `20260929142631829_2026.09.29 - Ala. Opp. - Singleton - FINAL.pdf`. Extraction succeeded: `pdf-text: 18 page(s), 25544 character(s)`. The initial display was terminal-truncated but included the ending argument and request for summary reversal or probable jurisdiction.
3. Repeated retrieval and extraction of that same September 29 PDF, displaying only 10,000 characters beginning at the substantive response. This exposed pages 1–3, including the continuing-injunction argument and express alternative request for Munsingwear vacatur, and the beginning of the merits response. Extraction again reported `pdf-text: 18 page(s), 25544 character(s)`.

## Validation

The completed cell is checked with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts validate data --cell data/cases/scotus/9026000118/events/evt-petition-disposition/predictions/codex-baseline/20261109T171058Z`. Validation is a local schema/completeness check, not substantive retrieval.
