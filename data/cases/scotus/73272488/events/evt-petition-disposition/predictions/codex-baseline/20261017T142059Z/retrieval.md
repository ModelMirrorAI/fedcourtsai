# Retrieval record

## Provisioned inputs

Read the event definition and case-level October 10, 2026 snapshot, context, document manifest, questions presented, petition discussion, and relevant passages of the lower-court opinion reproduced in the petition appendix. No realized-outcome file, other predictor output, or labeling-measurement artifact was read.

## Additional local context

- Read `metrics/statpack.md`: modern discretionary-cert disposition and originating-circuit cuts, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table.
- Read `metrics/statpack.json` to inspect available metadata and compute the exact prior-Term baseline risk-set pool. Selected matching sal-v4 baseline rows for Terms 2017–2024 and summed `prefix_est_grant_rate * prefix_weighted_resolved` over their summed `prefix_weighted_resolved`: 593 / 11,580 = 0.05120898100172712. No current-case row was queried.
- Read the prediction contract, JSON schemas, and local path/serialization helpers for output construction. Consulted the statistical-review checklist for denominator and stratum discipline.
- Ran `fedcourts paths --court scotus --docket 73272488 --event evt-petition-disposition --role predictor`. The first invocation failed because the default package cache was read-only; retrying with a writable temporary cache succeeded. The evaluator-only outcome was neither named as an input nor opened.

## Attempted external retrieval

1. `web.run` search query: `site.supremecourt.gov "Rule 10" "conflict" "certiorari"`. No usable result content returned.
2. `web.run` open of the generic official rules PDF at `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`. No usable document content returned.

Neither request named Abrams or sought any case disposition. No external substantive material was incorporated. No CourtListener MCP lookup or corpus `query`/`open-events` call was made, so there are no ranged-corpus transfer lines to report.
