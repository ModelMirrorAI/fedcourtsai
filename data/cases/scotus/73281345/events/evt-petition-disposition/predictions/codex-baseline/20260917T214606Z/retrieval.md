# Retrieval log

## Local aggregate context

- Read `metrics/statpack.md`: modern discretionary-cert disposition and originating-circuit sections, paid-segment relist and CVSG cuts, and the sal-v4 reached-band table. Other displayed sections were not used as cert anchors.
- Read `metrics/statpack.json`: inspected its keys and the 2024 segment structure, then pooled only the elevated risk-set values for the rendered prior Terms 2017-2024. Exact arithmetic: 484 / 2810 = 0.17224199288256228. No case-level corpus query or `open-events` call was made, and no ranged-read transfer line was emitted.
- Ran `uv run fedcourts paths --court scotus --docket 73281345 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; repeating with a writable cache under `/tmp` succeeded. This was path resolution, not a docket or outcome lookup.

## External general-legal-context retrieval

1. Web search for `site.ca10.uscourts.gov "Chavarria" "2025" "instrumentalities"`. The tool returned no usable result content.
2. CourtListener MCP `search(type="o", citation="140 F.4th 1257", num_results=3)`. Returned United States v. Chavarria, Tenth Circuit, filed June 16, 2025; cluster 10605317, opinion 11071905, appellate docket 23-2102.
3. Web open of the official Chavarria opinion PDF identified by that result: `https://www.ca10.uscourts.gov/sites/ca10/files/opinions/010111250704.pdf`. The tool returned no usable content; no facts were taken from this attempt.
4. CourtListener MCP `search_document(opinion_id=11071905, query="per se", snippet_size=1400)`. Read returned excerpts, including the limited motor-vehicle holding and constitutional-avoidance footnote near the conclusion.
5. CourtListener MCP `search_document(opinion_id=11071905, query="Certain items", snippet_size=600)`. Confirmed the opinion permits some classes to qualify as per se instrumentalities.

The external retrieval concerned only a cited lower-court comparator predating this petition. I did not search for Elkins's Supreme Court disposition, later docket history, or decision coverage. The empty web results were insufficient for verification; the CourtListener opinion excerpts supplied the relevant primary-source check instead.
