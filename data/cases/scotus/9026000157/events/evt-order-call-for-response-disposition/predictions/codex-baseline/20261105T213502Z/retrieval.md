# Retrieval record

## Provisioned inputs and local reference material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, the event definition, and the case-level `record/context.json`, `record/snapshots/2026-09-23.json`, `record/documents/documents.json`, `questions-presented.txt`, relevant portions of `petition.txt` and `appendix.txt`, and `record/same-question.json`. The same-question list was empty at its 0.5 threshold; that is not evidence that no related litigation exists. Consulted `metrics/statpack.md`, particularly the sal-v7 risk-set table and paid-segment relist, CVSG, and amicus cuts.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000157 --event evt-order-call-for-response-disposition --role predictor` — failed before lookup because the default uv cache was read-only.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts paths --court scotus --docket 9026000157 --event evt-order-call-for-response-disposition --role predictor` — succeeded, identifying the case and event paths. Did not open an outcome file.

No `fedcourts query` or `open-events` call was made, and no ranged-corpus-transfer line was returned. Validation is local schema/completeness checking, not a historical-case lookup.

## Web search attempt

One `web.run` call issued two targeted precedent queries:

- `site.supremecourt.gov "Atlantic Richfield" "separate lawsuit"`
- `site.supremecourt.gov "Puri" "Khalsa" "petition"`

The tool returned no usable results or source text. Neither query sought the subject petition's disposition; neither contributed substantive evidence.

## CourtListener MCP calls

1. `search(type="o", citation="844 F.3d 1152", num_results=2)` — one matching *Bibiji Kaur Puri v. Sopurkh Kaur Khalsa* opinion, filed January 6, 2017; cluster 4336459, opinion 4113720.
2. `search_document(opinion_id=4113720, query="neutral", snippet_size=1200)` — excerpts of the Ninth Circuit's neutral-principles analysis; 32 matches, 20 shown. Confirmed the opinion's corporate-control setting and its allowance for resolving pleaded secular claims without deciding religious doctrine.
3. `search(type="o", citation="590 U.S. 1", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` — overly broad citation matching returned 42 results and displayed an unrelated *GE Energy* case. Disregarded; did not paginate or read that opinion.
4. `search(type="o", case_name="Atlantic Richfield v. Christian", court="scotus", filed_after="2020-04-19", filed_before="2020-04-21", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` — one matching *Atlantic Richfield Co. v. Christian*, decided April 20, 2020; cluster 4746634, lead opinion 9889171.
5. `search_document(opinion_id=9889171, query="separate lawsuit", snippet_size=1500)` — one match confirming that the nature of the Montana supervisory-writ proceeding, rather than merely its issues, established finality for Supreme Court review. Used only as general vehicle context, not as a holding about Nevada's procedure.

No live lookup of this petition, its disposition, or subsequent history was attempted. No other cell's outputs, evaluator outcomes, or topic-label artifacts were read.
