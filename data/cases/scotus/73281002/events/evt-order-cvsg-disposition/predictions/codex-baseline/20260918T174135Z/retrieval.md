# Retrieval record

## Committed context

- Read `metrics/statpack.md`: modern discretionary-cert disposition counts, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term salience-band table. The calibration pool uses only Terms 2017-2024, strictly preceding the provisioned Term 2025. All-Term cuts are descriptive only.
- Computed the weighted mean of the displayed rounded high-band reached rates locally: denominator 898, rate 0.3495100223. No remote corpus read occurred.

## External retrieval

1. Web search: `site.supremecourt.gov Rule 10 considerations governing review certiorari conflict courts appeals`. The tool returned no usable result content. No target-case search was made.
2. Web open: the Cornell Supreme Court Rule 10 page. The tool returned no usable content. No legal proposition was taken from this attempt.
3. CourtListener MCP `search(type="o", citation="78 F.4th 377", num_results=2)`. Returned Barbara Tully v. Paul Okeson, Seventh Circuit, filed August 15, 2023, cluster 9420461, opinion 9556023, docket 22-2835. Used to examine the provisioned opposition's characterization of a distinct preexisting precedent.
4. CourtListener MCP `search_document(opinion_id=9556023, query="bound", snippet_size=750)`. Returned three excerpts. The relevant opening excerpt confirms that the court declined to treat Tully I as law of the case or binding reasoning and affirmed anew under the Twenty-Sixth Amendment. Did not retrieve later history or any disposition of the predicted case.

## Local operations

Read the task contract and relevant schema definitions, the event, snapshot, context, document manifest, questions presented, and substantive portions of the provisioned petition and combined respondent briefs. Ran `fedcourts paths --court scotus --docket 73281002 --event evt-order-cvsg-disposition --role predictor` successfully after moving the transient uv cache to `/tmp`. No `fedcourts query` or `open-events` calls occurred, so there are no ranged-corpus transfer lines to report. Validation is a schema check, not a source of prediction evidence.
