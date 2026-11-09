# Retrieval record

## Provisioned and committed material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`. Consulted the relevant cert sections of `metrics/statpack.md`: modern discretionary cert, originating circuit, relist, CVSG, amicus, capital, salience, and per-Term reached-band rates. No other cell's prediction or evaluation and no outcome file was read.

Read the event definition and case-level context, November 9 snapshot, questions presented, document manifest, petition argument and selected appendix passages, both staged Vide companion snapshots and their relationship manifest, and same-question list. Companion records were provisioned inputs, not live outcome lookups.

## Corpus calls

The initial `uv run fedcourts paths --court scotus --docket 9026000293 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help` failed because uv's default cache path was read-only. Retried with `UV_CACHE_DIR=/tmp/uv-cache`; path resolution and help then succeeded. Path resolution was run successfully twice and query help was displayed twice, with the second display restricted to its first 80 lines. The path tool did not expose an outcome path.

Executed:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 3
ranged corpus reads: 37 GET(s), 9699328 byte(s)
```

Returned Burford German Funding LLC v. financialright claims GmbH (25-1269), Roofing Designs by JR v. Royal American Construction (25-1367), and Pedro Jose Silva Ochoa v. United States (25-7569). All are prior-Term GVR records with two distributions. They lack opinion bodies in the returned rows and were used only as weak procedural examples, not substantive analogues. Their October 2026 grant dates precede this forward forecast. No current-case corpus lookup was made.

Also ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts pdf-text --help`; this only displayed the supported PDF-reading interface. No PDF was downloaded or extracted.

## Web attempts

All four web calls returned no usable visible content; none informed a factual conclusion:

1. Search query: `site.supremecourt.gov "Exxon Mobil" "CIMEX" "2026"`.
2. Combined search queries: `"Exxon Mobil Corp." "Corporación CIMEX" Supreme Court opinion` and `"152 F.4th 339"`.
3. Open the docket-linked October 5 Faiq amicus PDF: `https://www.supremecourt.gov/DocketPDF/26/26-293/428538/20261005173955936_Faiq%20cert%20op%20%20-%20final%20to%20printer.pdf`.
4. Repeat open of the same Faiq PDF; again no usable content.

No search requested Ashton's Supreme Court disposition, subsequent history, or decision coverage. No live current-case docket page was opened.

## CourtListener MCP

1. `search(type="o", case_name="Exxon Mobil Corp. v. Corporación CIMEX", num_results=3)`: returned one distinct precedent, cluster 10878536, opinion 11346053, docket 24-699, argued February 23 and decided June 23, 2026. Query id `f9446fd2`.
2. `read_document(opinion_id=11346053, chunk_index=[0,1], chunk_size=9000)`: read the syllabus and opening majority analysis. The case holds that Helms-Burton itself abrogates the relevant Cuban entities' sovereign immunity. Used to assess whether the petition's requested analogy really removes its independent TRIA obstacle. This is a different, preexisting case, not the target petition's outcome.

## Local validation

Run the contract's cell-scoped `uv run fedcourts validate data --cell` command with the writable uv-cache override. Validation checks only this output cell; it is not substantive legal retrieval.
