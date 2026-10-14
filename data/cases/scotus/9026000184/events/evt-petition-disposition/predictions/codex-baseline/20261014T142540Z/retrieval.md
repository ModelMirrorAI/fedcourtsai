# Retrieval record

## Committed base-rate context

- Read `metrics/statpack.md`: modern discretionary-cert disposition and circuit cuts, paid-segment relist and CVSG cuts, and the sal-v4 per-Term salience table.
- Read `metrics/statpack.json` for exact baseline reached-rate fields in the nine displayed prior Terms, 2017–2025. Pooled rate computed as the sum of rate times weighted denominator divided by the sum of weighted denominators: 643 / 12,877.
- No `fedcourts query` or `open-events` call was made. There is therefore no ranged-corpus-read stderr line to report. No local corpus was opened or refreshed.

## External legal context

1. Web search attempted with two queries: `Junger v Daley 209 F.3d 481 2000 source code First Amendment opinion` and `Christianson Colt 486 U.S. 800 1988 transfer law of case opinion`. The tool returned no usable content; no search result informed the forecast.
2. CourtListener MCP `search`, type `o`, citation `209 F.3d 481`, limit 2. Returned Junger, opinion 768337, and an unrelated Vance result. Used only Junger.
3. CourtListener MCP `read_document`, opinion 768337: *Junger v. Daley*, Sixth Circuit, April 4, 2000. Read the discussion and holding concerning source code, expression, functionality, and constitutional scrutiny. This is a prior authority, not this petition's outcome.
4. Web open attempted for Cornell's Supreme Court text of *Christianson v. Colt Industries Operating Corp.*, 486 U.S. 800 (1988). No usable content returned; no independently retrieved Christianson holding was relied upon.

## Local operations

Read the governing prompt and schemas, the cell's provisioned inputs, and path/serialization interfaces. Ran `fedcourts paths --court scotus --docket 9026000184 --event evt-petition-disposition --role predictor`; the first launch failed because the default package cache was read-only, and rerunning with a writable temporary cache succeeded. This was path resolution, not a corpus-prior lookup. Validation checks concern the produced artifacts only and do not supply forecast evidence.

No case-outcome lookup, live docket refresh, subsequent-history search, or other predictor/evaluator artifact read was performed.
