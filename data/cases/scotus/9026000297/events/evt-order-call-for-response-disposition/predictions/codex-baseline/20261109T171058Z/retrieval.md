# Retrieval record

## Local contract, inputs, and base rates

Read `.github/prompts/predict.md`, the prediction and tooling/flags schemas, the event definition, the October 19 snapshot, context, document manifest, questions presented, petition passages, relevant majority and separate-opinion passages in the amended appendix and separately staged decision, lower-court docket summary, and same-question list. Read `metrics/statpack.md`, specifically the modern-cert, originating-circuit, paid-segment relist, CVSG, amicus, and sal-v8 Term-band sections. No outcome, evaluation, other prediction, or qp-topics artifact was consulted.

The initial `uv run fedcourts paths --court scotus --docket 9026000297 --event evt-order-call-for-response-disposition --role predictor` failed because the default uv cache was read-only. Reissued as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000297 --event evt-order-call-for-response-disposition --role predictor`; returned the case, corpus, and event paths, without exposing an outcome path. No package was installed. Subsequent commands used the same cache/environment options.

## Corpus calls, including unsuccessful attempts

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help`: returned the structured-filter help. A second help call, piped through `tail -55`, read the remaining option details. Neither printed a ranged-read line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era modern --citation '563 U.S. 493' --limit 2`: rejected the invalid era `modern` and supplied the decade-token vocabulary. No ranged-read line.
3. Corrected as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '563 U.S. 493' --limit 2`: no matching rows; warned that only 200 SCOTUS rows in scope carried reporter citations and that an empty result was likely a coverage gap, not absence of the precedent. Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`: returned Goldman Sachs Bank USA v. Brown (25-1408), U.S. DOGE Service v. U.S. District Court (25-1103), and Berry v. United States (25-7026), with distribution counts 4, 2, and 5. These were a grant-selected, nonanalogous sample, not a denominator for grant probability. The clock filtered docket-Term cohorts and the returned grant dates included October/November 2026; this forward cell did not use them as a strictly pre-snapshot estimate. Stderr: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`.

## CourtListener MCP

1. `search(type="o", citation="969 F.3d 769", num_results=1)`: returned Henry v. Hulett, Seventh Circuit, August 11, 2020; cluster 4774392, opinion 4554739. Used only as historical context for certification cross-appeals.
2. `search_document(opinion_id=4554739, query="cross-appeal", snippet_size=1100)`: zero literal matches, because the text uses a different hyphen character.
3. `search_document(opinion_id=4554739, query="certification", snippet_size=1400)`: six matching excerpts, including the discussion that defendants needed a cross-appeal to challenge certification and had not filed one. This supports the procedural vehicle but is not a square holding on reversal undoing merger.

## Web attempts

1. One `web.run` call submitted the searches `site.supremecourt.gov Nutraceutical Corp Lambert Rule 23(f) nonjurisdictional 2019 opinion` and `site.supremecourt.gov Horne Flores institutional reform injunctions federalism 2009 opinion`. The tool supplied no usable visible result. No proposition was derived from an unseen result.
2. One `web.run` open attempted the official Supreme Court Nutraceutical opinion PDF, `opinions/18pdf/17-1094_bq7d.pdf`. Again no usable visible result was supplied; the attempted source was not relied on.

No search or request sought this petition's disposition or subsequent history. No own-case outcome was encountered. Validation is a local contract check, not substantive retrieval.
