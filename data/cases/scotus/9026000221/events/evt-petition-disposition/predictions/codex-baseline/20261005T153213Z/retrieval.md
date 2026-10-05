# Retrieval record

## Local inputs and historical context

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, flags, and tooling schemas.
- Read this cell's event definition, context, snapshot `2026-10-05.json`, document manifest, QP text, and selected portions of the petition, including the substantive cert arguments and Appendix A's decision under review.
- Read `metrics/statpack.md`: modern cert dispositions, paid-segment relist/CVSG cuts, and the sal-v4 Term table. Read corresponding aggregate fields in `metrics/statpack.json` to compute the unrounded prior-Term reached baseline. No case-membership labeling artifacts were read.
- Ran `git log -1 --format='%cs %h' -- metrics/statpack.md` to identify the committed pack's artifact vintage: September 28, 2026. This does not establish corpus-wide freshness.
- Ran `uv run fedcourts paths --court scotus --docket 9026000221 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; retrying with a writable temporary cache succeeded. This was path resolution, not corpus retrieval.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines were produced.

## Web attempts

The web tool returned no usable content for either call. No web-derived facts informed the prediction.

1. Search queries: `site.supremecourt.gov opinions 2023 Smith Arizona 22-899 statements true` and `site.supremecourt.gov opinions Ohio Clark 13-1352 very young children testimonial`.
2. Attempted to open the Smith slip opinion at `https://www.supremecourt.gov/opinions/23pdf/22-899_97be.pdf`.

## CourtListener MCP

1. `search(type="o", case_name="Ohio v. Clark", court="scotus", num_results=2)`. Returned the 2015 merits decision and an unrelated 2017 Clark cert denial. The latter did not inform this forecast.
2. `search_document(opinion_id=8136484, query="young children", snippet_size=650)`. Read majority-opinion passages on primary purpose, age, and the circumstances of the child's statements; did not conflate concurrence excerpts with the majority.
3. `search(type="o", case_name="Smith v. Arizona", court="scotus", filed_after="2024-06-01", filed_before="2024-07-01", num_results=1)`. Identified the June 21, 2024 decision, 602 U.S. 779.
4. `search_document(opinion_id=11066650, query="only if true", snippet_size=500)`. Verified the truth-use holding and that testimonial status remained a separate question.

No live retrieval concerned Purdy's own docket or outcome. The external sources were preexisting general precedent, not this case's later history.
