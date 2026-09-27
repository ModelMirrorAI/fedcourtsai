# Retrieval log

## Local materials beyond the provisioned case record

- Read the cell contract, repository instructions, and relevant prediction/tooling schemas.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist/CVSG cuts, and the sal-v4 prior-Term baseline reached table. A heading search also surfaced other section labels and table rows; no interim or merits rate was used as this cert cell's anchor.
- Inspected the top-level keys of `metrics/statpack.json` only; no case-level records were retrieved.
- Calculated the approximate denominator-weighted prior-Term baseline rate from the Markdown table using local Python: 0.050108883647798745, weighted denominator 12,720.
- Ran `uv run fedcourts paths --court scotus --docket 9026000296 --event evt-petition-arrival-disposition --role predictor`. The initial attempt failed because the default uv cache was read-only; the retry with a writable temporary cache and `--no-sync` succeeded. This resolves paths only and retrieves no case outcome.
- No `fedcourts query` or `open-events` call was made; there is no ranged-corpus transfer line to report.

## General web retrieval attempts

1. Search queries: `site.supremecourt.gov rules Rule 10 certiorari judicial proceedings` and `site.uscourts.gov Federal Rules Appellate Procedure 46 47 attorney discipline notice`. The web tool returned no usable result content.
2. Attempted opening of the Supreme Court's 2023 Rules PDF at the official filing-and-rules path. The web tool returned no usable content. No rule text or case-specific information was learned from either attempt.

## CourtListener MCP

1. `search(type="o", citation="390 U.S. 544", num_results=1, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`. Query 21009b0a returned an unrelated Bright v. Pennsylvania rehearing record. Excluded as irrelevant; not used as a prior.
2. `search(type="o", case_name="In re Ruffalo", court="scotus", num_results=2, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`. Query fc0b51d0 initially returned historical ancillary orders.
3. `get_more_results(query_id="fc0b51d0", num_results=3)`. Located the reported Ruffalo decision, 390 U.S. 544 (1968), combined opinion 107654. The returned opinion header identifies April 8, 1968 as its decision date; the search metadata carries a later date. No date-based inference depended on that discrepancy.
4. `search_document(opinion_id=107654, query="notice", snippet_size=500)`. Read the returned notice passages, particularly the majority's discussion at 550–552. Used only to check the general procedural-notice principle invoked by the petition.

No retrieval targeted Sethi's disposition or subsequent history. No outcome-revealing material concerning this petition was encountered.
