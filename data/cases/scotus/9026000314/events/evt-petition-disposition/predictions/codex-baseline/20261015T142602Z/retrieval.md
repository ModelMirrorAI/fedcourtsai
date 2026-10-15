# Retrieval record

## Provisioned inputs

Read the event definition, record/context.json, record/snapshots/2026-10-15.json, and the document manifest, questions presented, petition, and appendix under this case's record/documents/. No outcome file, other predictor output, or QP-topic artifact was read.

## Committed context and local tooling

- Read metrics/statpack.md: modern-cert disposition background, originating-circuit context, paid-segment relist/CVSG cuts, and the sal-v4 per-Term band table. Selected the baseline reached risk set for all displayed prior Terms, 2017–2025, and excluded 2026 from the anchor.
- Read metrics/statpack.json to obtain exact prefix_est_grant_rate and prefix_weighted_resolved values. A local jq calculation returned weighted resolved 12,877, grant-family count 643, and rate 0.04993399083637493. No case-level corpus rows were retrieved.
- Ran git log -1 --format='%h %cI' -- metrics/statpack.json: cf9ae960e, 2026-10-13T19:17:46Z. This dates the committed artifact, not the underlying corpus's latest pull.
- Ran uv run fedcourts paths --court scotus --docket 9026000314 --event evt-petition-disposition --role predictor. The default cache was read-only; retrying with a writable temporary cache succeeded. Read the path and serialization helpers to keep output within the cell contract.
- No fedcourts query or open-events call; no ranged corpus reads line. No CourtListener MCP lookup and no direct REST call.

## Web attempts

The web tool calls below returned no usable source text to this session. They did not change the forecast, and no external legal proposition is represented here as independently verified.

- Search: site.supremecourt.gov Rule 10 certiorari erroneous factual findings misapplication.
- Search: site.supremecourt.gov Norton Southern Utah Wilderness 2004 discrete agency action required.
- Open attempt: the official Supreme Court 2023RulesoftheCourt.pdf under filingandrules.
- Repeated open attempts: the official Supreme Court rules_guidance.aspx under filingandrules.
- Search: site.supremecourt.gov "Rule 10" "misapplication".
- Find attempt: "misapplication" in the official 2026RulesoftheCourt_WEB.pdf under filingandrules.

No search named this petition or sought its disposition, subsequent history, or decision coverage. No case outcome surfaced.
