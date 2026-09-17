# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-16.json`, `context.json`,
`event.yaml`, `documents/petition.txt`, `documents/questions-presented.txt`,
`documents.json`) and the committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   — returned recent denied SCOTUS rows ranked by recency (mostly substantive
   applications from summer 2026, plus a few petitions, including a pro se
   petitioner's). Nothing specific to this case or its questions; used only to
   confirm the shape of the recent denied population.
   stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`

## CourtListener MCP lookups

1. `search` (type `o`, court `ca6`, q "Gomez v. Ryan Rooker-Feldman", filed
   2025-11-01 to 2025-12-31) — 0 results.
2. `search` (type `o`, court `ca6`, docket_number `24-3840`) — 0 results.

Neither surfaced the Sixth Circuit's December 2, 2025 order, so the judgment
below is characterized from the petition's own statement. No lookup touched
this case's own SCOTUS docket or disposition.

## Web searches

None.
