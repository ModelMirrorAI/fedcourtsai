# Retrieval log

## Committed statistical context

- Read only the merits-docket section of `metrics/statpack.md` for the anchor (and the file's introductory metadata). Computed the eligible 2015-2024 pool from the displayed 2017-2024 rows with a local Python calculation: 360 disturbed / 516 parsed, 539 granted, 56 excluded. No cert-band anchor was used.
- No `fedcourts query` or `open-events` corpus lookup was made, so there is no ranged-corpus transfer line. `fedcourts paths --court scotus --docket 73277583 --event evt-brief-judgment --role predictor` resolved paths; it did not retrieve docket state or an outcome. Its outcome pathname was explicitly evaluator-only and was not opened.

## Web attempts: general precedents only

The following `web.run` calls returned no usable content or source excerpts:

1. Search: `site.supremecourt.gov opinions 2018 Kisor Wilkie genuinely ambiguous 18-15`.
2. Search in the same call: `site.law.cornell.edu supremecourt text 508 36 Stinson commentary authoritative`.
3. Search: `Kisor v Wilkie 2019 Supreme Court opinion 18-15 pdf`.
4. Search in the same call: `Stinson United States 508 U.S. 36 opinion commentary`.
5. Open the official Kisor slip opinion at `https://www.supremecourt.gov/opinions/18pdf/18-15_9p6b.pdf`; no content was returned.

None searched Beaird or its subsequent history. No web material informed the forecast.

## CourtListener MCP

1. `search(type="o", case_name="Kisor v. Wilkie", court="scotus", filed_before="2020-01-01", num_results=3, fields=["caseName", "dateFiled", "citation", "cluster_id", "opinions", "absolute_url"])` returned the June 26, 2019 merits decision, 588 U.S. 558, cluster 4632953, opinion 4410206, and a separate 2018 cert grant. The merits result included the opening opinion snippet, not its substantive ambiguity discussion.
2. `search_document(opinion_id=4410206, query="genuinely ambiguous", snippet_size=700)` returned HTTP 429, with a reported 39-second wait; no passage was retrieved.
3. A later retry, `search_document(opinion_id=4410206, query="genuinely ambiguous", snippet_size=450)`, again returned HTTP 429, with a reported 13-second wait; no passage was retrieved.

No other MCP lookup, live case retrieval, argument retrieval, or outcome retrieval was made. No direct REST fallback was attempted. Legal analysis rests principally on the provisioned briefs and lower-court appendix, with the limited Kisor identity confirmation described above.
