# Retrieval log

## Local materials beyond the provisioned record

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating circuit, paid relist and CVSG cuts, and the `sal-v4` prior-Term reached-band table. Local arithmetic pooled the printed 2017–2024 baseline rates with their weighted denominators; n = 11,580 and approximate rate = 5.12025%.
- Read the task instructions and schemas for prediction, tooling feedback, and agent flags.
- Ran `uv run fedcourts paths --court scotus --docket 73500222 --event evt-petition-disposition --role predictor`. The first invocation failed because the default cache was read-only; rerunning with a temporary writable cache succeeded. This resolves paths, not corpus content.
- No `fedcourts query` or `open-events` lookup was performed. There are no ranged-corpus transfer lines to report.

## Web attempts

All three calls returned no visible results or document text; none supplied evidence or exposed a case outcome.

1. A batched search for `site.uscourts.gov Federal Rules Civil Procedure Rule 54 costs prevailing party` and `Stanley University Southern California 178 F.3d 1069 1079 1080 chilling costs`.
2. A search for `site.uscourts.gov "Rule 54" "Costs Other Than Attorney"`.
3. An attempted open of `https://cdn.ca9.uscourts.gov/datastore/opinions/2014/02/25/11-17608.pdf` as a potential historical costs authority. No content returned; I did not identify or rely on an opinion from this attempted open.

## CourtListener MCP

1. `search(type="o", citation="178 F.3d 1069", num_results=1)` returned *Stanley v. University of Southern California*, filed June 2, 1999, cluster 7077586, lead opinion 6982455. This was a historical authority lookup, not a search for this petition or its subsequent history.
2. `search_document(opinion_id=6982455, query="chilling", snippet_size=1800)` returned the costs discussion at reporter pages 1079–80. I used its holding that failure to consider indigency and chilling effects justified finding an abuse of discretion to check the petition's description of Ninth Circuit law.

No live docket, current-petition outcome, other predictor output, evaluation artifact, or topic-label artifact was consulted.
