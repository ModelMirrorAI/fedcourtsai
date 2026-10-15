# Retrieval record

## Provisioned material

Read `event.yaml`, `record/context.json`, `record/snapshots/2026-10-15.json`, `record/documents/documents.json`, `questions-presented.txt`, the substantive petition, and relevant appendix sections, particularly the disciplinary order, show-cause order, and Sethi declaration. These are the cell's provisioned inputs.

## Committed statistical context

- Read `metrics/statpack.md`: modern-cert disposition, originating-circuit, paid relist, CVSG, capital marking, salience, and prior-Term band tables; heading discovery also surfaced descriptive interim/merits section captions, which were not used as cert anchors.
- Read selected fields in `metrics/statpack.json`, including prior-Term `sal-v4` baseline risk-set rates and weighted denominators. A local jq calculation pooled Terms 2017–2025: 643 / 12,877 = 0.04993399083637493.
- `git log -1 --format='%h %cI' -- metrics/statpack.md` returned artifact commit `cf9ae960e`, dated October 13, 2026, 19:17:46 UTC. No live corpus freshness was inferred from this timestamp.
- No `fedcourts query` or `open-events` call was made; there are no ranged-corpus transfer lines.

## General web attempts

1. Search: `site.supremecourt.gov Rule 10 certiorari rarely granted erroneous factual findings misapplication properly stated rule law`. No usable result content returned.
2. Open: Cornell's Supreme Court Rule 10 page, `https://www.law.cornell.edu/rules/supct/rule_10`. No usable page content returned. Neither attempt supplied evidence used in the forecast.

## CourtListener MCP

1. `search(type="o", citation="390 U.S. 544", num_results=1)` returned an unrelated *Bright v. Pennsylvania* record; discarded as a citation-search mismatch.
2. `search(type="o", case_name="In re Ruffalo", court="scotus", filed_before="1969-01-01", num_results=2)` returned Ruffalo post-decision orders, not the merits opinion; not relied on for the notice doctrine.
3. `search(type="o", case_name="In re Ruffalo", court="scotus", filed_after="1968-04-01", filed_before="1968-05-01", num_results=1)` returned zero results.
4. `get_more_results(query_id="149f757a", num_results=3)` returned the Ruffalo merits opinion (opinion 107654, 390 U.S. 544) and older procedural orders. Its text states decision on April 8, 1968, while search metadata uses May 27, explaining the date-filter miss. Only the merits-opinion notice doctrine informed the forecast.
5. `search_document(opinion_id=107654, query="notice", snippet_size=700)` retrieved passages on fair notice, a new charge derived from testimony, and the separate opinions. These confirmed the petition's general doctrinal premise without deciding its application to Sethi.

No lookup sought this case's cert disposition, current docket, subsequent history, another predictor's output, or outcome-bearing labeling artifacts.
