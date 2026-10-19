# Retrieval log

## Local reference material

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term reached-band table. Read `metrics/statpack.json` for unrounded prior-Term high-band figures. Selected Terms 2017–2025 only for the scored anchor; calculated weighted grant-family numerator 344 and denominator 971. No `fedcourts query` or `open-events` call was made, so no ranged-corpus transfer line exists.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json`: artifact commit `ac757d745`, October 19, 2026, 05:54:06 UTC. This does not establish corpus-wide freshness.
- Read the required prompt and schemas, path and serialization helpers, and the statistical-review checklist for artifact preparation. Ran `fedcourts paths` with the supplied court, docket, event, and predictor role; no outcome was opened.

## Web attempts

- One search call with queries `site.supremecourt.gov opinions 2011 Arizona United States 11-182 immigration preemption` and `site.supremecourt.gov Rule 10 considerations governing review certiorari` returned no usable content.
- One open attempt for `https://www.law.cornell.edu/rules/supct/rule_10` returned no usable content.
- Neither attempt concerned this petition's disposition or subsequent history. No web result informed the forecast.

## CourtListener MCP

1. `search(type="o", citation="567 U.S. 387", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: identified *Arizona v. United States*, decided June 25, 2012, including lead opinion 9500790.
2. `search_document(opinion_id=9500790, query="discretion", snippet_size=450)`: returned seven excerpts from that majority opinion concerning federal immigration-enforcement and removal discretion. Used only for general legal context.
3. `search(type="o", citation="589 U.S. 191", num_results=1, fields=["caseName", "dateFiled", "citation", "absolute_url", "id"])`: identified *Kansas v. Garcia*, decided March 3, 2020. The response warned that `id` is not a search result field.
4. `search_document(opinion_id=4731814, query="priorities", snippet_size=700)`: returned no matches in the short document available at that identifier. No substantive holding was inferred from this unsuccessful passage lookup.

## Statistical check

A read-only reviewer checked the prior-Term arithmetic and claim conditioning using only the prompt, schema, committed statpack, and provisioned context. It was explicitly barred from outcomes, other predictions, topic artifacts, external retrieval, and file writes. It confirmed 344/971 for the high-band anchor and 57/164 for the CVSG comparison, and identified a rounding correction for the terminal two-relist comparison: use 198/487 = 40.7%, rather than adding the displayed rounded shares. I checked those bucket counts in the JSON and applied the correction. No other statistical blocker was reported. This was a statistical consistency check, not an independent legal forecast.
