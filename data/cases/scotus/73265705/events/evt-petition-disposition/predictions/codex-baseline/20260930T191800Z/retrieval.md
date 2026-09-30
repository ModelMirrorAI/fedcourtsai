# Retrieval record

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-09-30.json`, document metadata, and `questions-presented.txt`. Read relevant introductions, argument and vehicle sections of `petition.txt` and the combined `brief-in-opposition.txt`, including the federal respondent's argument. The reply and amici were observed only as docket entries. No outcome file or other predictor's output was read.

## Committed base-rate material

Consulted `metrics/statpack.md`: modern discretionary-cert dispositions, circuit context, paid-segment relist and CVSG cuts, and the sal-v4 segment-by-Term table. Consulted `metrics/statpack.json` to pool only the elevated reached fields for displayed Terms 2017–2024. Calculation: sum(rate times weighted denominator) divided by sum(weighted denominator), giving 484 / 2,810. Other displayed Term rows were not used as the anchor.

No `fedcourts query` or `open-events` lookup was performed; there is no ranged-corpus transfer line to report. `fedcourts paths --court scotus --docket 73265705 --event evt-petition-disposition --role predictor` resolved the allowed paths. Its first invocation failed on a read-only default uv cache; a temporary-cache override succeeded.

## General legal retrieval

1. Web search: `site.uscode.house.gov 35 USC 314 determination whether to institute final nonappealable`. The tool returned no usable content.
2. Web open of the House U.S. Code preliminary-edition page for title 35, section 314, using its granule identifier. The tool returned no usable content. Neither web call supplied facts used in the forecast; neither sought this case or its outcome.
3. CourtListener MCP `search`, opinion type, citation `579 U.S. 261`, one result requested, fields case name/date/citation/path/opinions. Returned Cuozzo Speed Technologies, LLC v. Lee, June 20, 2016, cluster 3214886; majority opinion 9824227.
4. CourtListener MCP `search_document`, opinion 9824227, query `shenanigans`, context 1,500 characters. Read the majority's passage discussing review of extra-statutory agency action in final-decision review and the contrasting bar on institution-related statutory challenges. Used only as general preexisting legal context.

No current docket lookup, subsequent-history search, direct CourtListener REST request, or target-case disposition retrieval occurred.
