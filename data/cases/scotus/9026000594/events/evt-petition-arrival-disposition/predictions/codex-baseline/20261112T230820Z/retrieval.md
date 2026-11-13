# Retrieval record

## Provisioned and repository inputs

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, and `schemas/agent_tooling.schema.json`; the arrival event; the case-level snapshot `2026-11-06.json`; context; document manifest; QP and petition; the matching lower-court judgment and docket summary; the appendix's en banc judgment, portions of the panel opinion, and administrative-stay order; the official `Vide` companion snapshot `26-589.json` and relation manifest; and the empty same-question list. Consulted `metrics/statpack.md`, including the sal-v8 prior-Term reached-rate table and paid-segment relist, CVSG, and amicus cuts. No evaluator outcome, other prediction, evaluation, or QP-label artifact was opened.

An initial overly broad shell file listing produced filenames, including unrelated outcome-file paths, but no outcome-file contents were read or used. Subsequent reads were restricted to the contract, schemas, statpack, and this case's provisioned record. Initial attempts to read `schemas/tooling.schema.json` and `schemas/flags.schema.json` failed because those names do not exist; the correct `agent_` schema names were then used.

## CLI attempts and corpus lookups

All successful CLI calls below used `UV_NO_CACHE=1` to avoid the default read-only uv cache. No package installation was attempted.

1. `uv run fedcourts paths --court scotus --docket 9026000594 --event evt-petition-arrival-disposition --role predictor` initially failed to initialize `/home/codexcell/.cache/uv` because the filesystem there is read-only. Retried successfully with `UV_NO_CACHE=1`; it resolved the case and event paths without reading an outcome.
2. `uv run fedcourts query --help` with `UV_NO_CACHE=1` returned structured-filter usage. No corpus transfer line.
3. `uv run fedcourts query --court scotus --disposition gvr --era modern --decided-before 2026 --limit 4` with `UV_NO_CACHE=1` failed: `modern` is not a permitted decade token. The error listed valid eras; corrected to `2020s`. No transfer line was reported for the rejected query.
4. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 4` with `UV_NO_CACHE=1` succeeded. Returned Roybal v. Griffith, No. 25-442; Harrington v. Martin, No. 25-1348; Burford German Funding v. financialright claims, No. 25-1269; and Roofing Designs by JR v. Royal American Construction, No. 25-1367. The combined tool output was truncated, so its initial transfer line was not retained in the visible response; I do not invent its byte count. These are route examples, not subject-matched funding priors. November 9, 2026 dates on two examples are permissible general context in this forward cell, not subsequent history of the target case.
5. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2025 --limit 3` with `UV_NO_CACHE=1`, piped to `jq` for a compact projection, returned Monsanto v. Salas, No. 24-1097; Monsanto v. Johnson, No. 24-1098; and Petersen v. Doe, No. 24-449. All showed June 30, 2026 GVRs, illustrating that a bare-year filter applies the docket-Term rather than a calendar-day boundary. No rates were inferred from this selected sample.

   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`

6. Repeated the corrected lookup from item 4 with a compact `jq` projection to retain the returned rows and transfer line. Same four results.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

7. `uv run fedcourts query --court scotus --citation '591 U.S. 657' --decided-before 2026 --limit 2` with `UV_NO_CACHE=1`, piped to a compact `jq` projection. No results. The CLI warned that only 195 SCOTUS rows carried any reporter citation and that citation filtering matches a case's own citations, not a citation graph. This is a coverage limitation, not evidence that Little Sisters of the Poor did not exist or lacked a companion. No sparse-filter retry.

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

## Web attempts

Each `web.run` attempt below returned no visible content, source identifier, or usable result. Nothing from these attempts entered the probability; none queried the target case or its disposition.

1. Batched search queries: `site.supremecourt.gov Department of Education California 2025 Tucker Act grants` and `site.supremecourt.gov National Institutes of Health American Public Health Association 2025 grants`.
2. Search: `Department of Education v California April 4 2025 Supreme Court 24A910 official`.
3. Search: `site.supremecourt.gov/opinions "25A103" "Tucker"`.
4. Open attempt for the Supreme Court's Department of Education slip opinion: `https://www.supremecourt.gov/opinions/24pdf/24a910_f2bh.pdf`.

## CourtListener MCP

1. Opinion search, `case_name="Department of Education v. California"`, `filed_before="2026-11-06"`, `num_results=3`. Returned the April 4, 2025 Supreme Court opinion at 604 U.S. 650 in duplicate clusters, plus the First Circuit decision. Used the Supreme Court match only; selected opinion 10839607 from cluster 10373019, docket 24A910. The official download URL was the one attempted through web above.
2. Opinion search, `court="scotus"`, `q='"National Institutes of Health" "American Public Health"'`, `filed_before="2026-11-06"`, `num_results=2`, with selected metadata fields. Returned zero results. Did not infer anything substantive from the empty search.
3. `read_document(opinion_id=10839607, chunk_index=0, chunk_size=14000)`. Returned the opening chunk of the Supreme Court's Department of Education opinion, including its jurisdiction and Tucker Act discussion and separate writings. Used as independently retrieved legal context, not as a disposition of the target case.
4. Opinion search, `citation="145 S. Ct. 2658"`, `court="scotus"`, `num_results=2`, with selected metadata fields. Returned zero results. The NIH authority remains identified as cited in the provisioned petition, not independently verified.

## Completion check

Ran the contract's cell validator after writing these outputs; validation is a local schema/completeness check, not a substantive case retrieval.
