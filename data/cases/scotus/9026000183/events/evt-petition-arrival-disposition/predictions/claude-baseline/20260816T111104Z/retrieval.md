# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-16.json`, `event.yaml`,
`record/context.json`, `record/documents/` petition + questions-presented,
`documents.json`) and the committed `metrics/statpack.md`:

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition granted --limit 5`
   — shape check on recent SCOTUS grants (counsel profile, distribution counts
   at grant: 2–22).
   stderr: `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
2. `uv run fedcourts query --court scotus --limit 200` piped to grep for a
   Detwiler row — none found in the returned rows. stderr was not captured on
   this call (discarded by the pipe), so its `ranged corpus reads` line is not
   recorded here; assume egress comparable to call 1.

## CourtListener MCP

3. `search` (dockets, court=scotus, q=`Detwiler "Mid-Columbia"`) — 0 results.
4. `search` (dockets, court=scotus, q=`Detwiler`) — 0 results.
5. `search` (opinions, q=`Detwiler "Mid-Columbia"`) — found the Ninth Circuit
   published opinions (2025-09-23 and 2026-04-15); confirms the companion case
   exists below but no SCOTUS petition docket is visible on CourtListener as of
   today.

No web searches. No retrieval touched this case's own disposition (none exists;
the petition is pending with a response due 2026-09-11).
