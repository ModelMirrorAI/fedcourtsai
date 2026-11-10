# Retrieval record

## Provisioned and repository inputs

Read `.github/prompts/predict.md`, the prediction and feedback schemas, the event definition, `record/context.json`, `record/snapshots/2026-11-09.json`, `record/documents/documents.json`, the questions presented, substantive and selected appendix passages of the petition, relevant portions of the provisioned decision below, the lower-court docket extract, and `record/same-question.json`. Both the petition/appendix and the decision below have disclosed truncation. Consulted the modern-cert, originating-circuit, paid-segment relist/CVSG/amicus cuts and sal-v8 risk-set table in `metrics/statpack.md`; used the frozen cert anchor rather than the current-Term row. Repository path discovery and `git status --short` were operational checks only; no other cell output or evaluator outcome was opened.

## CLI attempts and corpus lookups

1. `uv run fedcourts paths --court scotus --docket 9026000341 --event evt-petition-disposition --role predictor` failed before execution because the default uv cache under `/home/codexcell/.cache/uv` is read-only. No record was retrieved.
2. Retried as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000341 --event evt-petition-disposition --role predictor`. It returned the case, corpus and event paths and identified the outcome as evaluator-only; no outcome path or outcome content was read. The environment override and `--no-sync` were used for subsequent CLI operations, without installing anything.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` read the structured-filter interface. A later identical help invocation was piped through `sed -n '65,145p'` to inspect the citation, era, disposition and cutoff options. Neither fetched priors or printed transfer statistics.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '591 U.S. 71' --era 2020s --limit 2` returned no rows and warned that reporter-citation coverage is sparse. This is not evidence that Liu is absent as precedent. No repeat of the sparse citation filter was attempted.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition gvr --era 2020s --limit 2` returned Heidi Cid v. United States, No. 26-5123 (grant date November 9, 2026, distribution count 1), and Burford German Funding LLC v. financialright claims GmbH, No. 25-1269 (grant date October 19, 2026, distribution count 2). Display was piped through `cut -c 1-4500`; the compact rows fit. Neither had an opinion body. These are general route examples, not securities-law analogues, companion cases or a statistical sample from which to estimate this case's probabilities. No `--full` hydration was requested and no own-case corpus lookup was made.

   `ranged corpus reads: 27 GET(s), 7077888 byte(s)`

## Web attempt

One `web.run` call attempted two primary-source searches: `site.supremecourt.gov opinions Sripetch 2026 disgorgement` and `site.supremecourt.gov opinions Liu Securities Exchange Commission 2020 investors treasury`. The tool surfaced no results or source text. The absence supplied no legal evidence; the Sripetch opinion was then retrieved through CourtListener. These searches did not name the petition being forecast or seek its disposition.

## CourtListener MCP calls

1. `search(type="o", case_name="Sripetch", court="scotus", num_results=3, fields=["caseName","dateFiled","citation","absolute_url","snippet","id"])` returned the June 4, 2026 Sripetch Supreme Court opinion, cluster 10870059. The tool warned that some requested search fields were not present; this did not prevent the cluster lookup.
2. `get_endpoint_item(endpoint_id="clusters", item_id=10870059, fields=["id","case_name","date_filed","sub_opinions","scdb_id"])` identified opinion 11337516.
3. `read_document(opinion_id=11337516, chunk_index=0, chunk_size=11000)` retrieved its syllabus and opening discussion, including the holding against a pecuniary-loss prerequisite and the express reservation of related questions. Only that chunk, not the whole opinion, was read.
4. `get_endpoint_item(endpoint_id="clusters", item_id=10775540, fields=["case_name","date_filed","sub_opinions"])` confirmed the provisioned January 16, 2026 lower-court opinion match and identified opinion 11242127.
5. `search_document(opinion_id=11242127, query="TJOFLAT, Circuit Judge", snippet_size=1900)` returned the panel heading and the transition from the majority's affirmance to the opening of Tjoflat's dissent. Used to distinguish its pleading-defect focus from a demonstrated dissent on the questions presented; no complete-dissent reading is claimed.
6. `search_document(opinion_id=11337516, query="Treasury", snippet_size=550)` returned four snippets, including the main opinion's reservation of the infeasible-distribution question and its discussion of the concern about Treasury-directed penalties. This corroborated that the petition raises an issue not resolved by the no-pecuniary-loss holding.
7. `search_document(opinion_id=11242127, query="would vacate", snippet_size=800)` returned no matches. No inference about the dissent's proposed remedy is drawn from that literal-search miss.

No search for this petition's Supreme Court disposition, subsequent history, decision coverage, or another predictor's output was attempted. The lower-court affirmance and Sripetch's disposition are permissible pre-decision legal context, not the target petition's outcome.
