# Retrieval record

## Provisioned inputs and local reference material

Read the event definition, `record/context.json`, `record/snapshots/2026-11-05.json`, `record/documents/documents.json`, `questions-presented.txt`, the petition body and relevant bound-appendix passages, and `record/same-question.json`. The same-question list was empty and was not used to infer the absence of related litigation. No live docket lookup or search about this petition's disposition was made.

Read `.github/prompts/predict.md`, the prediction and tooling schemas, and the modern-cert, paid relist, CVSG, amicus, and sal-v6 per-Term sections of `metrics/statpack.md`. Used the frozen context anchor rather than the current-Term band row. Local path discovery and `git status --short` did not read another prediction or evaluation. No outcome file or `data/qp-topics/` material was read.

## CLI calls, including unsuccessful attempts

1. `uv run fedcourts paths --court scotus --docket 9026000526 --event evt-petition-disposition --role predictor` — failed before execution because uv's default cache was on a read-only filesystem.
2. `uv run fedcourts query --help` — same default-cache failure; no corpus lookup occurred.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000526 --event evt-petition-disposition --role predictor` — succeeded and identified the case and event paths; outcome remained evaluator-only.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` — succeeded; read structured-filter usage. A later repeat, `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help | tail -72`, read the remaining options. Neither queried case records.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition denied --decided-before 2026 --limit 3` — rejected because `modern` is not an era token; usage supplied decade-token vocabulary. No transfer statistics were printed.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3` — succeeded. Transfer: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`. Returned Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), and Ryan O'Donnell v. Chicago (25-1098), all denials dated October 19, 2026, before the present forward prediction. The bare-year filter bounds the corpus's derived year, not necessarily the disposition's calendar year. These were not double-jeopardy analogues and were not used as an empirical grant-rate sample. No full opinion hydration was requested.

The mandated cell validation is a local output check, not a case retrieval.

## Web attempts

1. `web.run` search query `site.supremecourt.gov opinions McElrath Georgia 2024 acquittal Scott procedural dismissal` — returned no visible result or usable source text.
2. `web.run` open of the official Supreme Court McElrath opinion PDF at the path `/opinions/23pdf/22-721_j426.pdf` — returned no visible source text. No external McElrath text was used; the discussion rests on the provisioned petition.

Neither call searched for Mitchell or his petition's outcome.

## CourtListener MCP calls

1. `search(type="o", court="scotus", citation="437 U.S. 82", num_results=2)` — broad results (22 matches), initially Ramey and Medina-Vasquez denials, not the target Scott merits opinion. Disregarded as nonresponsive.
2. `search(type="o", court="scotus", q='caseName:"United States v. Scott" AND dateFiled:[1978-01-01 TO 1978-12-31]', num_results=1)` — two matches; first was the rehearing-denial compilation, cluster 9019620. Did not use it for the merits rule.
3. `search(type="o", court="scotus", q='caseName:"United States v. Scott"', filed_after="1978-06-01", filed_before="1978-07-01", num_results=2)` — zero matches. No inference that the precedent was absent.
4. `get_more_results(query_id="10bac3df", num_results=2)` — retrieved Scott, cluster 109895, 437 U.S. 82, majority opinion 9842021. Search metadata used an October 2 date, while the combined-opinion opening identifies the merits decision as June 14, 1978; no significance was attached to the metadata date.
5. `search_document(opinion_id=9842021, query="close", snippet_size=650)` — one match, the opening paragraph confirming that Scott's dismissal occurred at the close of all evidence. This materially informed the downward grant adjustment.
6. `search_document(opinion_id=9842021, query="unrelated", snippet_size=650)` — five excerpts, including the distinction between actual acquittals and defendant-requested dismissals on grounds unrelated to factual guilt at pages 98–99. Used to assess the petition's claimed distinction, not to infer this case's eventual disposition.
