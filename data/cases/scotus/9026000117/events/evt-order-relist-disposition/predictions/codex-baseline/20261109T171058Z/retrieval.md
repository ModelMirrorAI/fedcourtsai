# Retrieval record

## Local inputs and reference material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; the assigned event; case-level context, snapshot, documents manifest, questions presented, and relevant jurisdictional-statement and appendix excerpts; and `record/same-question.json`. No related-case docket was retrieved.

Beyond those provisioned inputs, read the committed `metrics/statpack.md` paid-segment relist, CVSG, amicus, modern-cert and salience-band sections and corresponding `metrics/statpack.json` counts. Pooled prior-Term high-band counts reproduce 269/772 = 0.3484455958549223. Also inspected the local corpus-service timeout documentation after a slow query; it supplies no case facts.

## CLI calls

Commands below were invoked with `uv run`. After the first cache-permission failure, subsequent commands used `UV_CACHE_DIR=/tmp/uv-cache` and `--no-sync` so no package installation was requested.

1. `uv run fedcourts paths --court scotus --docket 9026000117 --event evt-order-relist-disposition --role predictor` initially failed because the default uv cache was read-only. Retried as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000117 --event evt-order-relist-disposition --role predictor`; it resolved the expected paths without reading an outcome.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` returned the structured-filter interface.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era modern --limit 3` was rejected: `modern` is not an allowed decade token. No corpus result or transfer line was produced.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 3` completed with no matching rows. Stderr: `ranged corpus reads: 1071 GET(s), 280756224 byte(s)`. This absence is not treated as evidence that summary reversal is unavailable.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 3` returned Burford German Funding, 25-1269; Roofing Designs by JR, 25-1367; and Pedro Jose Silva Ochoa, 25-7569, all GVR rows, with no opinion bodies. Stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`. None is a substantive redistricting analogue; they received no case-specific predictive weight. This forward cell did not require a replay clock; the optional Term filter further narrowed the query.

## CourtListener MCP

1. `search(type="o", citation="146 S. Ct. 1377", num_results=3)` returned zero results. This sought the June 2026 stay cited in the provisioned statement, not the pending appeal's disposition.
2. `search(type="o", citation="146 S. Ct. 1131", num_results=3)` returned an unrelated 1973 Court of Claims opinion, Milton S. Kronheim & Co. Rejected as a false citation match; its opinion body was not read.
3. `search(type="o", court="scotus", case_name="Louisiana v. Callais", filed_before="2026-07-22", num_results=3)` returned the April 29, 2026 decision and its May 4 revision. Selected revised opinion ID 11320154, docket 24-109. This is a separate, pre-filing precedent, not the outcome of 26-117.
4. `search_document(opinion_id=11320154, query="just as well", snippet_size=650)` returned the majority's comparator-map requirement and a passage from Kagan's dissent.
5. `read_document(opinion_id=11320154, chunk_index=[0,12], chunk_size=8000)` supplied opening/syllabus material and the majority's distinction of the 2023 Allen ruling and application of the updated framework. These passages support the doctrinal discussion; no later history of this appeal was requested.

## Web attempts

1. Searched `site.supremecourt.gov opinions 2025 Louisiana Callais April 2026 146 1131`; no usable result was returned.
2. Searched `"Louisiana v. Callais" "2026" "1131"` and `"Allen" "Milligan" "1377" "2026"` together, targeting the two pre-filing authorities cited in the statement. No usable result was returned and no web page was opened. No own-case disposition search was made.

## Validation

Validate only the assigned output cell using the prompt's validator; the validation result is reported on completion. No `usage.json` or `retrieval_log.json` is written by the predictor.
