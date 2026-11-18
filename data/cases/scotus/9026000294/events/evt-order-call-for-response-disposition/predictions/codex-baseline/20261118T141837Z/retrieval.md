Provisioned inputs consulted: event.yaml; record/snapshots/2026-11-17.json; record/context.json; record/documents/documents.json, questions-presented.txt, petition.txt, and lower-court-docket.txt; record/related/related.json, 26-292.json, and 26-293.json. These are baseline inputs, not external retrieval. Contract and output schemas were also read.

Additional committed statistical context: metrics/statpack.md, specifically modern discretionary-cert dispositions, originating-circuit rates, paid-segment relist/CVSG/amicus cuts, and the sal-v8 per-Term band table. metrics/statpack.json was opened to inspect its top-level structure; no case-level outcome or prediction artifact was read.

Corpus and CLI calls, including failed attempts:

1. `uv run fedcourts paths --court scotus --docket 9026000294 --event evt-order-call-for-response-disposition --role predictor` — failed before execution because uv could not write its default cache. No lookup results or transfer line.
2. `uv run fedcourts query --help` — same cache failure; no lookup results or transfer line.
3. `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 9026000294 --event evt-order-call-for-response-disposition --role predictor` — succeeded, reporting the case and event paths and identifying the outcome as evaluator-only. No outcome was read.
4. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` — succeeded; inspected supported structured filters.
5. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 4` — returned Robinhood Markets v. Sodha (25-944), Goldman Sachs Bank USA v. Brown (25-1408), U.S. DOGE Service v. U.S. District Court (25-1103), and Berry v. United States (25-7026). The Term mask selected earlier docket Terms; these were forward-mode procedural examples, not a rate estimate or subject-matched sample. Robinhood's returned row records a CVSG and three distributions. No opinion bodies were requested.
   `ranged corpus reads: 40 GET(s), 10485760 byte(s)`

CourtListener MCP calls (lower-court material only):

1. `search`: type `o`, court `ca2`, citation `152 F.4th 339`, filed_before `2026-11-18`, num_results 3, requested fields caseName/dateFiled/citation/cluster_id/opinions/absolute_url/snippet. Returned zero results.
2. `search`: type `o`, court `ca2`, case_name `Havlish`, filed_after `2025-01-01`, filed_before `2026-11-18`, num_results 5, same requested fields. Returned the August 26, 2025 panel decision (cluster 10660852, opinion 11127439) and March 19, 2026 rehearing writings (cluster 10811059, opinion 11277807). A missing-field warning concerned the requested top-level snippet; opinion-level snippets were present.
3. `read_document`: opinion_id 11127439, chunk_index 0, chunk_size 14000. Read the consolidated case identification, procedural distinction between attachment and turnover, and opening holdings.
4. `read_document`: opinion_id 11277807, chunk_index 0, chunk_size 14000. Read the rehearing order, five dissenters' identification, Nardini's short concurrence, and the beginning of Sullivan's dissent.
5. `read_document`: opinion_id 11127439, chunk_index [2, 3], chunk_size 14000. Read portions of the majority's immunity and executive-recognition analysis, approximately slip pages 18–30. The combined tool transcript display was truncated; the targeted search below checked the material distinction used in the forecast.
6. `read_document`: opinion_id 11277807, chunk_index 5, chunk_size 14000. Read the end of Menashi's dissent, including its distinction between recognizing Afghanistan and determining DAB's current status, and Cabranes and Calabresi's closing statement.
7. `search_document`: opinion_id 11127439, query `Finally, we emphasize`, snippet_size 2200. Returned one match spanning the majority's distinction between executive recognition of a state's legal existence and judicial interpretation of which entities enjoy statutory immunity (slip pages 30–31).

Source links: https://www.courtlistener.com/opinion/10660852/havlish-v-taliban-aliganga-v-taliban/ and https://www.courtlistener.com/opinion/10811059/havlish-v-taliban-aliganga-v-taliban/ . No web search, live Supreme Court docket fetch, forecast search, or own-case Supreme Court disposition lookup was attempted.
