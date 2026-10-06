# Retrieval log

## Provisioned case inputs

- Read `event.yaml`, `record/context.json`, and `record/snapshots/2026-10-05.json` for this cell. No filed-document directory was present.
- Did not read outcomes, other predictors' outputs, or labeling-measurement artifacts.

## Committed historical context

- Read the modern discretionary-cert, originating-circuit, paid relist-count, paid CVSG-status, and sal-v4 per-Term segment sections of `metrics/statpack.md`.
- Read the schema and Term segment fields of `metrics/statpack.json`. Calculated the baseline reached rate over displayed Terms 2017-2025 as 638/12720 = 0.05015723270440252. Excluded the cell's own Term 2026.
- No `fedcourts query` or `open-events` calls were made; there are no ranged-corpus transfer lines to report.

## Live retrieval attempts

1. `web.run` direct open of the snapshot-linked September 25, 2026 petitioner letter, attempted twice. Both calls returned no usable content and supplied no facts:

   `https://www.supremecourt.gov/DocketPDF/26/26-43/425720/20260925165931280_2026.09.25%20Letter%20re%20DC.pdf`

2. `mcp__courtlistener.search` with `type="o"`, `court="ca5"`, `q="\"Buenrostro\""`, `filed_after="2026-02-05"`, `filed_before="2026-02-07"`, and `num_results=3`. This sought the pre-petition lower-court opinion identified in the snapshot. Result: count 0, results empty; query id `9f778292`. No opinion text was retrieved.

No broad web searches, live Supreme Court docket lookups, or requests for this case's disposition or subsequent history were made. No outcome-revealing material was encountered.

## Operational checks

- `uv run fedcourts paths --court scotus --docket 9026000043 --event evt-petition-disposition --role predictor`: initially failed on a read-only default cache location; succeeded with the cache redirected to `/tmp/uv-cache`.
- Consulted the prediction, agent-flags, and agent-tooling schemas and the repository's path/identifier helpers for output construction.
