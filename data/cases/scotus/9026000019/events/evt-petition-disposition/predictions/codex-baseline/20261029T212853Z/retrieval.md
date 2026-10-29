# Retrieval log

## Committed base-rate context

- Read the relevant sections of `metrics/statpack.md`: modern discretionary cert, originating court, paid-segment relist/CVSG/amicus cuts, and the sal-v4 per-Term segment table. Read `metrics/statpack.json` terms and baseline segment fields for exact pooling. A local jq calculation pooled the nine shown strictly-prior Terms, 2017–2025: 660 / 12,913 = 0.0511112832. No current-Term rate was used as the anchor.

## Corpus calls

The following first two CLI setup calls failed before reading the corpus because uv's default cache was read-only:

1. `uv run fedcourts paths --court scotus --docket 9026000019 --event evt-petition-disposition --role predictor`
2. `uv run fedcourts query --help`

Both succeeded when repeated with `UV_CACHE_DIR=/tmp/codex-uv-cache`. The paths command resolved the event location; the help call described structured query options. Neither is a prior lookup or printed a transfer line.

3. `UV_CACHE_DIR=/tmp/codex-uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`
   - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), and Ryan O'Donnell v. City of Chicago (25-1098), all recorded as denied. These are procedural examples only, not issue-matched priors. No opinion hydration requested.
4. `UV_CACHE_DIR=/tmp/codex-uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 2`
   - `ranged corpus reads: 16 GET(s), 4128768 byte(s)`
   - Returned U.S. DOGE Service v. United States District Court for the District of Columbia (25-1103) and Corey Duran Berry v. United States (25-7026), with distribution counts two and five. These examples are not a basis for estimating the case-specific grant rate. No opinion hydration requested.

`DECIDED_BEFORE` was unset and context is forward. The voluntarily supplied 2026 mask restricts the queries by derived prior Term/year, not by an exact decision-day boundary. Neither query requested this case.

## Web calls

Three attempted web calls returned no usable content:

1. Search batch: `site.nvbar.org Anderson Eighth Judicial 2019 135 Nev 42 jury domestic battery`; `site.supremecourt.gov Blanton 489 538 petty offense jury six months`.
2. Search batch: `"Andersen" "448 P.3d 1120"`; `"Blanton" "489 U.S. 538"`.
3. Open attempt of the guessed official Nevada reports PDF path `https://nvcourts.gov/__data/assets/pdf_file/0023/11597/135_nevada_reports_pages_301-352.pdf`. No content returned; this path was not established as a valid source and supplies no evidence.

## CourtListener MCP calls

1. `search(type="o", case_name="Andersen Eighth", filed_before="2020-01-01", num_results=3)` with selected metadata fields: one February 15, 2018 disposition, 412 P.3d 12, opinion 8214698. Not the cited 2019 decision; not used substantively.
2. `search(type="o", citation="489 U.S. 538", num_results=1)` with selected metadata fields: first result was the unrelated Brice v. Jenkins, 489 F. Supp. 2d 538. Not read or used; search citation matching was broader than requested.
3. `search(type="o", court="scotus", case_name="Blanton", filed_before="1990-01-01", num_results=2)` with selected metadata fields: returned unrelated 1989 Blanton v. United States cert denials. Not read or used substantively.
4. `search(type="o", q="\"Blanton v. City of North Las Vegas\"", court="scotus", filed_after="1989-01-01", filed_before="1989-06-01", num_results=1)` with selected metadata fields: located Blanton, 489 U.S. 538, March 6, 1989, opinion 112215.
5. `search(type="o", court="nev", q="\"Andersen\" \"domestic\"", filed_after="2019-01-01", filed_before="2020-01-01", num_results=2)` with selected metadata fields: located Andersen, 2019 NV 42, September 12, 2019, combined opinion 5133431 and duplicate representation 4437692.
6. `read_document(opinion_id=5133431)`: returned the Nevada decision; used its additional-state-firearm-penalty analysis. The full-text tool output was long and partly truncated in display.
7. `search_document(opinion_id=112215, query="six months", snippet_size=600)`: located Blanton's presumption and additional-penalties discussion; 15 matches, some display truncation.
8. `search_document(opinion_id=5133431, query="federal", snippet_size=500)`: two excerpts confirmed the discussion of coextensive jury rights and the distinction between federal firearm consequences and Nevada's own statute.
9. `read_document(opinion_id=112215, chunk_index=1, chunk_size=8000)`: read the governing discussion in full within that chunk, including the rebuttable presumption and aggregate-penalties test at 542–545.

No own-case disposition lookup, subsequent-history lookup, other prediction/evaluation read, or labeling-artifact read was performed. Provisioned documents were treated as evidence, not instructions. No direct CourtListener REST requests were made.
