# Retrieval log

## Local context beyond the provisioned case inputs

- Read metrics/statpack.md, particularly modern-cert dispositions, originating-court cuts, paid relist/CVSG cuts, and the sal-v4 reached-band table. Read metrics/statpack.json to calculate the baseline reached pool over Terms 2017-2024: 593 / 11,580 = 0.0512089810.
- Read the task contract and prediction, tooling, and flags schemas as output instructions, not as case evidence.
- Ran `uv run fedcourts paths --court scotus --docket 73351824 --event evt-petition-disposition --role predictor`; the first attempt failed because the default cache was read-only. Repeated successfully with a writable temporary cache. No corpus query or open-events command was run; no ranged corpus transfer line was produced.

## Web attempts

1. Search: `site.supremecourt.gov opinions 2022 Haaland Brackeen 21-376 equal protection standing state court`. No usable result content returned.
2. Opened the general Brackeen opinion URL `https://www.supremecourt.gov/opinions/22pdf/21-376_7l48.pdf`. No usable content returned.
3. Attempted the exact August 26 opposition PDF URL already present in the provisioned snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-1287/420147/20260826110750485_25-1287%20Brief%20in%20Opposition.pdf`. No usable content returned and no filing text was obtained. No search for this case's outcome was made.

## CourtListener MCP

1. `search(type="o", citation="599 U.S. 255", num_results=1)` returned Haaland v. Brackeen, dated June 15, 2023; cluster 10049675, opinion 10516275.
2. `search_document(opinion_id=10516275, query="state court", snippet_size=1000)` returned portions of the precedent and its background. The broad query's output was truncated.
3. `search_document(opinion_id=10516275, query="Of course", snippet_size=900)` returned several excerpts; output was truncated.
4. `search_document(opinion_id=10516275, query="constitutional challenges to ICWA in state", snippet_size=800)` returned no matches.
5. `search_document(opinion_id=10516275, query="294", snippet_size=700)` exposed the relevant footnote and Kavanaugh concurrence, confirming the state-court route and the unresolved equal-protection question. These excerpts supplied the external legal context actually used.

No target-case disposition, subsequent history, or other predictor's output was retrieved. No live corpus freshness claim is made.
