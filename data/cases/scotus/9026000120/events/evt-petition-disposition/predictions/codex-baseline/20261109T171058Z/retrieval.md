# Retrieval record

## Local inputs and calibration

Consulted `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, the supplied event definition, and this case's provisioned record: November 9 snapshot, context, same-question list, document manifest, questions presented, petition including available opinion appendix, opposition, and reply. Consulted `metrics/statpack.md`, particularly the paid-segment relist, CVSG, amicus, and sal-v8 prior-Term reached-band tables. No other prediction, evaluation, outcome record, or topic-labeling artifact was consulted.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000120 --event evt-petition-disposition --role predictor` failed because the default uv cache was read-only. Reissued as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000120 --event evt-petition-disposition --role predictor`; succeeded and returned the case, corpus, and event paths. No outcome path was opened.
2. `uv run fedcourts query --help` encountered the same cache failure. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded; a second help call piped to `tail -85` displayed the cutoff and transport options. These help calls returned no case priors or transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2026 --limit 4` was refused because `modern` is not a valid decade token. No priors or transfer line were returned.
4. Corrected query: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4`.
   Transfer: `ranged corpus reads: 36 GET(s), 9437184 byte(s)`.
   Returned Goldman Sachs Bank USA v. Brown (25-1408, four distributions), U.S. DOGE Service v. U.S. District Court (25-1103, two), Berry v. United States (25-7026, five), and Blanche v. Ozurumba (25-1343, two), each labeled granted. This is a grant-selected procedural sample, not a subject-matter match or an estimate of grant odds. The bare-year filter masks by derived year and does not necessarily mean each returned disposition predates January 1, 2026; this cell is forward, and these unrelated priors do not establish any outcome for this petition.

## CourtListener MCP

1. `search(type="o", citation="446 U.S. 719", num_results=1)` returned an unrelated Datasouth Computer Corp. opinion, citation 719 F. Supp. 446. Disregarded as a reporter-number mismatch; no text read.
2. `search(type="o", court="scotus", q="\"446 U.S. 719\"", num_results=1)` returned the correct Supreme Court of Virginia v. Consumers Union of the United States, Inc., decided June 2, 1980, opinion/cluster 110273.
3. `search_document(opinion_id=110273, query="enforcement", snippet_size=550)` returned excerpts distinguishing protected rulemaking from direct enforcement authority. Used to check the doctrinal distinction, not to learn anything about this petition's disposition.

## Web attempts

1. One `web.run` search call contained the queries `site.loc.gov "Supreme Court of Virginia" "Consumers Union" "legislative" "1980"` and `site.ca5.uscourts.gov "Minton" "legislative immunity"`. The tool returned no visible result or source material.
2. `web.run` open request for `https://www.loc.gov/item/usrep446719/` likewise returned no visible source material. Neither attempt informed the estimate.

No search for this petition's disposition, subsequent history, or decision coverage was made. No live docket refresh was needed. Validation is a local output-contract check, not substantive retrieval.
