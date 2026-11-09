# Retrieval record

## Baseline and local reference material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; the event definition; the provisioned case-level context, November 9 snapshot, document manifest, questions presented, relevant portions of petition/opposition/reply and appendix searches, lower-court docket summary, and same-question list. Consulted `metrics/statpack.md`, especially modern cert, paid-segment relist/CVSG/amicus cuts, and prior-Term sal-v8 band rates. No outcome file, other prediction, evaluation tree, or qp-topics artifact was read. No target-case disposition search was made.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000116 --event evt-order-relist-disposition --role predictor` failed before execution because the default uv cache was read-only. No packages were installed.
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 9026000116 --event evt-order-relist-disposition --role predictor` succeeded, returning case, corpus, and event paths without an outcome path.
3. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` returned the structured-filter help. It was read again using `UV_NO_CACHE=1 COLUMNS=160 uv run --no-sync fedcourts query --help | head -65` for legibility.
4. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 4` returned Burford German Funding v. financialright claims, No. 25-1269; Roofing Designs v. Royal American Construction, No. 25-1367; Silva Ochoa v. United States, No. 25-7569; and Garcia v. Hobbs, No. 25-901. All were GVR rows, with no opinion bodies. The 2026 Term mask was voluntarily conservative on this forward cell, and the returned cert dates precede the prediction date. These are illustrative, disposition-selected priors, not an estimated grant frequency.

   Exact transfer line: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`.

## Web calls

5. `web.run` search for `site.supremecourt.gov Rule 11 certiorari before judgment imperative public importance` returned no content or usable source identifier.
6. `web.run` open of the official Supreme Court `filingandrules/2023RulesoftheCourt.pdf` returned no content or usable source identifier. Neither web attempt informed the prediction. Neither sought the target's disposition.

## CourtListener MCP calls

7. Opinion search with citation `602 U.S. 1`, limit 2, fields `caseName,dateFiled,citation,absolute_url,id`: returned Alexander v. South Carolina State Conference of the NAACP, May 23, 2024, with cluster links 10600091 and 9506541. The response warned that `id` was not a search-result field.
8. `search_document(opinion_id=9506541, query="good faith", snippet_size=450)` returned zero matches. This was an identifier mistake: the search-result URL identified a cluster, not an opinion.
9. `search_document(opinion_id=9506541, query="presumption", snippet_size=600)` returned one unrelated historical Hawaii intoxication-law excerpt. Disregarded entirely; it was not about this case or its outcome.
10. `get_endpoint_item(endpoint_id="clusters", item_id=9506541, fields=["id","case_name","sub_opinions"])` confirmed the Alexander cluster and identified opinion 9973154.
11. `search_document(opinion_id=9973154, query="presumption", snippet_size=450)` returned Alexander syllabus, majority and separate-opinion excerpts addressing legislative good faith and disentangling race and politics. Used only as general precedent, with the dissent's competing view of factual deference also visible. No target-case subsequent history was retrieved.

## Completion

The cell validator is run locally after writing the outputs; its result is recorded in the final response. Local file inspection and schema checks are not substantive external retrieval.
