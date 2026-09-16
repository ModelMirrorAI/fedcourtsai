# Retrieval beyond the provisioned record

- Read the committed `metrics/statpack.md`: modern discretionary-cert disposition and originating-court tables, paid-segment relist and CVSG cuts, and sal-v4 reached-band table. Inspected top-level keys of `metrics/statpack.json` for vintage metadata. Computed a weighted approximation from the displayed baseline reached rates for Terms 2017–2024: 5.12025%, denominator 11,580. No individual corpus rows were queried.
- Web search: `Philadelphia Newspapers Inc v Jerome 434 U.S. 241 1978 Supreme Court opinion`. The tool returned no usable result content.
- Web open of the government-reporter PDF path `https://www.govinfo.gov/content/pkg/USREPORTS-434/pdf/USREPORTS-434-241.pdf` returned no usable content. No reliance placed on this attempt.
- CourtListener `search(type="o", citation="434 U.S. 241", num_results=1)` returned an unrelated 2006 district-court case matching volume/page numbers. Disregarded that result; did not read its full opinion.
- CourtListener `search(type="o", court="scotus", case_name="Philadelphia Newspapers", filed_before="1980-01-01", num_results=3)` located the 1978 opinion, along with historical 1974 and 1979 results. Only the 1978 decision informed the forecast.
- CourtListener `read_document(opinion_id=9427020)` returned the complete 1,628-character per curiam opinion in Philadelphia Newspapers, Inc. v. Jerome, 434 U.S. 241 (1978). Used to assess the petition's alternative request for clarification of the state court's grounds.

No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines were produced. No search for this petition's outcome, current docket, subsequent history, or decision coverage. The docketed September 11 supplemental brief was not retrieved.

Contract/schema reads and `fedcourts paths` were operational, not factual retrieval. The first paths invocation failed because the default uv cache was read-only; repeating with a writable temporary cache succeeded.
