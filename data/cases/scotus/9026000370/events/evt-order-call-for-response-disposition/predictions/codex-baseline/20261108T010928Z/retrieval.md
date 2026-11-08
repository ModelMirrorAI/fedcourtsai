# Retrieval record

## Local baseline and reference material

Read `.github/prompts/predict.md`, the prediction and tooling schemas, the event definition, case-level `record/context.json`, and `record/snapshots/2026-11-06.json`. Consulted `documents.json`, `questions-presented.txt`, substantive petition passages, the lower-court opinion's header and relevant reasoning, `lower-court-docket.txt`, and the appendix's opening/identification of the matched opinion. Consulted the modern cert, paid-segment relist/CVSG/amicus, and sal-v8 per-Term portions of `metrics/statpack.md`. No other predictor outputs, evaluator outcomes, or topic-label artifacts were read.

Operational calls: `uv run fedcourts paths --court scotus --docket 9026000370 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` initially failed on the read-only default uv cache. Reissued with `UV_NO_CACHE=1`; paths resolved and query help printed. Query help was also consulted with a trailing `tail -85` display. This environment override avoids caching; it does not install dependencies.

## Corpus lookups

1. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3`.
   Returned recent grant rows. The combined terminal response was truncated, and its transfer-statistics line was not retained in the visible response. I do not reconstruct unknown transfer counts. The immediately repeated lookup below records the same result compactly.
2. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3`, piped through a Python JSON-field display.
   `ranged corpus reads: 0 GET(s), 0 byte(s)`
   Returned Scanlan v. Coalition for Open Democracy, 26A512, an interim application with zero distributions; Association for Education Fairness v. Montgomery County Board of Education, 26-12, three distributions; and Department of Justice v. McNutt, 26-204, two distributions. All were labeled granted, with no CVSG or available opinion. These heterogeneous selected grants are not a denominator and supplied no independent numerical calibration.
3. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --citation '542 U.S. 953' --limit 2`, piped through the same compact display.
   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   No rows. The tool warned that only 200 SCOTUS rows in scope carry reporter citations, so the empty result reflects a sparse column and cannot disprove the petition's LePage's account. No sparse-filter retries were made.

## Web attempts

Each of the following `web.run` calls returned no usable result text, source identifier, or document content; none informed a factual claim:

1. Search queries: `site.ca6.uscourts.gov Collins Inkjet Eastman Kodak 781 264 2015 differential pricing` and `site.ca9.uscourts.gov Cascade Health PeaceHealth 515 F.3d 883 discount attribution`.
2. Search queries: `Collins Inkjet Corp Eastman Kodak 781 F.3d 264 2015 opinion` and `Cascade Health PeaceHealth 515 F.3d 883 opinion Ninth Circuit`.
3. Open attempt: official Sixth Circuit opinion at `https://www.ca6.uscourts.gov/opinions.pdf/15a0045p-06.pdf`.

No web query sought this petition's outcome or subsequent history.

## CourtListener MCP

1. `search(type="o", citation="781 F.3d 264", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`.
   Found Collins Inkjet Corporation v. Eastman Kodak Co., decided March 16, 2015; combined opinion ID 2982827. This is the historical Sixth Circuit comparator, not the petition being predicted.
2. `search_document(opinion_id=2982827, query="economic equivalent", snippet_size=1000)`.
   One match, confirming the cost-based test for differential-pricing-only ties and its explanation in terms of competitive alternatives.
3. `search_document(opinion_id=2982827, query="affirm", snippet_size=700)`.
   Three matches, including the conclusion affirming the preliminary injunction. This qualified, rather than merely repeated, the petition's characterization of the comparator.

No live Supreme Court docket, same-case disposition, or subsequent-history retrieval was attempted. No outcome-revealing material surfaced.
