# Retrieval record

## Local reference material and CLI setup

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json` for the output contract; inspected applicable instruction-file locations without finding additional instructions.
- Read `metrics/statpack.md`: modern discretionary-cert disposition and originating-court cuts; paid-segment relist, CVSG, and amicus cuts; salience-band table and the prior-Term sal-v7 reached-band table. Used the provisioned context's frozen 0.051512996760685784 anchor as authoritative.
- `uv run fedcourts paths --court scotus --docket 9026000157 --event evt-order-call-for-response-disposition --role predictor` failed before path resolution because the default uv cache was read-only.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000157 --event evt-order-call-for-response-disposition --role predictor` succeeded and confirmed the case and event paths. The evaluator-only outcome was not opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned the structured-filter interface.

## Corpus calls

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era roberts --disposition granted --limit 4`
   - Rejected: `roberts` is not a valid era; eras are decade tokens. No corpus transfer line was printed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026-09-23 --limit 4`
   - Returned four granted substantive interim applications: People Not Politicians v. Onder; National Republican Congressional Committee v. Brown; National Park Service v. National Trust for Historic Preservation; Trump v. California. These are not cert-petition comparators and did not inform the grant estimate. Used a voluntary snapshot-day cutoff although this is a forward cell.
   - `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '443 U.S. 595' --limit 1`
   - No result. The CLI warned that only 200 scoped rows carried reporter citations and that this is a sparse own-citation column. No inference of precedent absence was drawn.
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

## Web call

One `web.run` search invocation contained these two queries:

- `site.supreme.justia.com Jones v Wolf 443 U.S. 595 1979 neutral principles`
- `site.supreme.justia.com Serbian Eastern Orthodox Diocese Milivojevich 426 U.S. 696 1976`

The tool returned no usable results or source payload. Neither search supplied evidence. No search sought this petition's disposition, current docket, or subsequent history.

## CourtListener MCP calls

1. `search(type="o", citation="844 F.3d 1152", num_results=3)` returned one published Ninth Circuit decision, Bibiji Kaur Puri v. Sopurkh Kaur Khalsa, filed January 6, 2017; cluster 4336459, opinion 4113720. The opening describes a dispute over control of Sikh-affiliated nonprofit entities.
2. `search_document(opinion_id=4113720, query="We are unaware", snippet_size=1000)` returned one passage confirming Puri's willingness to apply secular legal rules beyond property disputes when the ministerial exception does not apply and doctrinal controversies need not be resolved. Used to check the broader side of the legal disagreement, not to infer this petition's outcome.

## Boundaries

The case's factual and procedural account comes from the provisioned record. No current Supreme Court docket, later opposition, case outcome, other predictor output, evaluation, or labeling artifact was retrieved. No opinion bodies were hydrated through corpus `--full`, and no corpus output was used as a cert-frequency sample.
