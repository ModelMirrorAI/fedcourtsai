# Retrieval record

## Provisioned and local context

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; the event definition; the case-level context and November 5 snapshot; document metadata, questions presented, petition, and appendix; and the empty same-question match list. Consulted `metrics/statpack.md`, especially modern cert dispositions, paid-segment relists, CVSGs, amici, and the prior-Term `sal-v7` reached-band table. No other prediction, evaluation, outcome file, or QP-labeling artifact was consulted.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000157 --event evt-petition-disposition --role predictor` — failed before running because the default uv cache was read-only.
2. `uv run fedcourts query --help` — failed for the same cache reason.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000157 --event evt-petition-disposition --role predictor` — succeeded; confirmed case and event paths. Did not access the evaluator-only outcome.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` — succeeded; reviewed supported structured filters. Repeated help once with its last 85 lines displayed to inspect the remaining options.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --limit 3` — returned three recent grants. The combined terminal display was truncated, so the original transfer-stat line was not retained in my visible output. I repeated the identical query below to obtain a compact, fully readable result and transfer report. No opinion bodies were requested.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --limit 3 | jq -c '{case_id,case_name,docket_number,disposition,distribution_count,cvsg_date,date_cert_granted}'` — returned *Scanlan v. Coalition for Open Democracy*, 26A512 (an application, zero distributions); *Association for Education Fairness v. Montgomery County Board of Education*, 26-12 (three distributions); and *Department of Justice v. McNutt*, 26-204 (two distributions). The two cert grants were dated October 19, 2026. These are weak procedural comparisons only, not subject-matter analogues.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

7. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition denied --limit 3 | jq -c '{case_id,case_name,docket_number,disposition,distribution_count,cvsg_date,date_cert_denied}'` — returned *Guardado v. Florida*, 26A623; *Guardado v. Comerford*, 26A634; and *Lopez Jaime v. Blanche*, 26A637. All were applications with zero distributions and no cert-denial date. I did not treat this application sample as a cert-denial prior.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

No replay clock was required: the provisioned mode is forward and `decided_before` is null. The queried populations were filtered to dispositions, not this unresolved petition.

## General-authority web search

One `web.run` call contained two searches: `site.supreme.justia.com Jones v Wolf 443 U.S. 595 neutral principles` and `site.ca9.uscourts.gov Puri Khalsa 844 F.3d 1152 2017`. The tool returned no usable result content. No factual adjustment rests on this attempted search. Neither query sought the target case or its disposition.

## CourtListener MCP

1. `search(type="o", citation="844 F.3d 1152", num_results=1, fields=["caseName","citation","dateFiled","id","absolute_url","snippet"])` — found *Bibiji Kaur Puri v. Sopurkh Kaur Khalsa*, decided January 6, 2017, cluster 4336459. Warned that some requested fields were unavailable; the citation, date, and case name were returned.
2. `search(type="o", citation="178 F.4th 193", num_results=1, fields=["caseName","citation","dateFiled","absolute_url","opinions","cluster_id"])` — no results. The petition's description of that newer authority was not independently confirmed.
3. `get_endpoint_item(endpoint_id="clusters", item_id=4336459, fields=["case_name","sub_opinions","date_filed"])` — returned sub-opinion 4113720 and confirmed the 2017 date.
4. `search_document(opinion_id=4113720, query="property", snippet_size=800)` — retrieved passages discussing neutral principles, church property, and non-property disputes. Confirmed the opinion's broader secular-rules approach, subject to doctrinal and ministerial-exception limitations. Used only that general legal context; did not retrieve the target petition's disposition or history.

## Validation

The final cell is checked with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts validate data --cell data/cases/scotus/9026000157/events/evt-petition-disposition/predictions/codex-baseline/20261105T213502Z`. This is a local schema/completeness check, not retrieval of outcome information.
