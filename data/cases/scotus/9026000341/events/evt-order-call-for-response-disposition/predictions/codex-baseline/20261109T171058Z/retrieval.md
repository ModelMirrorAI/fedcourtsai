# Retrieval record

No lookup sought this petition's own disposition, subsequent history, or coverage of its decision. No other prediction or evaluation was read. The case-specific evidence came from the provisioned record; the live docket was not fetched.

## Local inputs and base rates

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the flags and tooling schemas, the event definition, the October 23 snapshot, document metadata, questions presented, relevant petition and lower-opinion sections, lower-court docket summary, context, and same-question list. Consulted `metrics/statpack.md`, especially its modern-cert, relist, CVSG, amicus, and sal-v8 prior-Term band sections. These were local reads with no corpus-transfer line.

## CLI diagnostics and corpus lookups

1. `uv run fedcourts paths --court scotus --docket 9026000341 --event evt-order-call-for-response-disposition --role predictor` failed before execution because the default uv cache was read-only. No retrieval occurred. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; it resolved the case, corpus, and event paths successfully. No evaluator-only file was opened.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned the structured-filter interface. No transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition gvr --decided-before 2026 --limit 3` was rejected: `modern` is not a valid decade-token era. No transfer line. The error supplied the complete supported vocabulary; the query was corrected rather than abandoned.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition gvr --decided-before 2026 --limit 3` returned Burford German Funding (25-1269), Roofing Designs (25-1367), and Pedro Jose Silva Ochoa (25-7569). These are generic grant-vacate-remand route examples, not subject-matched securities precedents. No opinion bodies were requested. The Term filter admitted prior-Term dockets whose displayed grant dates fell in October 2026; those dates still preceded this cell's October 23 baseline. These rows were not treated as a grant-rate sample.

   `ranged corpus reads: 37 GET(s), 9699328 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '591 U.S. 71' --decided-before 2026 --limit 1` returned no rows and warned that only 200 SCOTUS rows in scope carry reporter citations. This failed to identify Liu and was not evidence that Liu is absent as authority. No repeat sparse-filter lookup was made.

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

## Web attempts

1. One `web.run` call attempted searches for `site.supremecourt.gov "Sripetch" "2026" opinion` and `site.supremecourt.gov "Liu" "Treasury" "2020"`. The tool returned no usable content or source references.
2. A second call attempted `Sripetch Supreme Court disgorgement 2026 opinion` and `Liu SEC 2020 591 U.S. 71 opinion`. Again no usable content or source references returned.
3. An open attempt at `https://www.supremecourt.gov/opinions/25pdf/25-466_5i26.pdf` returned no usable content. This was an unverified candidate URL, not a successfully identified or read opinion. No factual proposition is attributed to it.

## CourtListener MCP

`search(type="o", court="scotus", citation="146 S. Ct. 1403", num_results=2)` returned count 0, query id `a9c8b306`. This did not verify the petition's description of Sripetch. No direct REST fallback was attempted. That description is used only as the petition's representation, with an explicit confidence discount in `reasoning.md`.

## Completion check

The cell is checked using `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000341/events/evt-order-call-for-response-disposition/predictions/codex-baseline/20261109T171058Z`. This is local artifact validation, not external retrieval.
