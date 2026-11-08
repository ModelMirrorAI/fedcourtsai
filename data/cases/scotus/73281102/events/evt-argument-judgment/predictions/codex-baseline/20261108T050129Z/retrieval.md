# Retrieval record

## Local inputs and reference material

Read `.github/prompts/predict.md`, the prediction, flags, and tooling schemas, the event definition, the provisioned case-level context, the dated snapshot, the document manifest, the questions presented, the lower-court decision and docket summary, substantive sections of both merits briefs and both merits replies, and the argument transcript and deterministic argument features. No provisioned text was marked empty or OCR-derived. The Court-appointed amicus's argument was available in the transcript; his brief was not separately staged or externally retrieved.

Beyond the provisioned inputs, consulted the merits and per-Justice sections of `metrics/statpack.md`, the corresponding `merits`, `justice_votes`, and `authorship` objects in `metrics/statpack.json`, and portions of `metrics/README.md`. Computed the eligible pre-grant-Term pools locally with Python. No corpus priors query, `open-events` query, remote corpus read, or another cell's prediction was attempted. No own-case outcome or postdecision coverage was sought or encountered.

## CLI and environment calls

- `uv run fedcourts paths --court scotus --docket 73281102 --event evt-argument-judgment --role predictor` initially failed because the default uv cache under `/home/codexcell/.cache/uv` was read-only.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 73281102 --event evt-argument-judgment --role predictor` succeeded and confirmed the case and event paths. It did not expose an outcome path or perform a corpus lookup. No `ranged corpus reads` line was printed.
- Cell validation uses the same writable temporary cache. These are local contract/path/schema checks, not legal-information retrieval.

## Web attempts

The following `web.run` attempts were limited to general statutory text and a historical precedent, not this case. Every attempt returned no visible result or page content, so none supplied information used in the prediction:

1. One batched search call with queries `site.uscode.house.gov 28 USC 2241 custody violation Constitution laws`, `site.uscode.house.gov 18 USC 3632 time credits shall transfer eligible prisoners prerelease`, and `site.loc.gov Preiser Rodriguez 411 U.S. 475 parole habeas 1973`.
2. An open call for `https://uscode.house.gov/view.xhtml?edition=2023&num=0&req=granuleid%3AUSC-2023-title28-section2241`.
3. An open call for `https://www.govinfo.gov/content/pkg/USCODE-2024-title28/html/USCODE-2024-title28-partVI-chap153-sec2241.htm`.

## CourtListener MCP

1. `search(type="o", citation="411 U.S. 475", court="scotus", num_results=1)`: query ID `4e1ffe9e`; returned an irrelevant Howard v. Wainwright result and indicated two matches. Not relied upon and not paginated.
2. `search(type="o", case_name="Preiser v. Rodriguez", court="scotus", filed_before="1974-01-01", num_results=2)`: query ID `1b711306`; returned the May 7, 1973 Supreme Court decision, 411 U.S. 475, cluster 108772, including lead opinion 9425260. Used only to identify the historical precedent already cited in the supplied briefs.
3. `search_document(opinion_id=9425260, query="parole", snippet_size=800)`: returned eight matching passages. The factual passages at printed pages 478–481 confirm that restoring credits entitled prisoners to release from prison on parole. This supports the limited analogy discussed in reasoning.md. No subsequent history or citing-case search was made.

All successful external legal retrieval concerned a 1973 opinion. No information revealing the outcome of Maxwell's case surfaced.
