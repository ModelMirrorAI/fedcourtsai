# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `record/documents/petition.txt`,
`record/documents/questions-presented.txt`, `record/documents/documents.json`,
`event.yaml`) and the committed `metrics/statpack.md`:

## Corpus

1. `uv run fedcourts query --court scotus --citation "411 U.S. 792" --limit 8`
   — returned no rows.
   stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
   stderr note: citations filter covers 161 of 590,339 SCOTUS rows and matches
   a case's own reporter cites only — the empty result is a coverage gap, not
   evidence of no similar precedent. Not retried per the sparse-filter
   guidance.

## CourtListener MCP

2. `search` (type=o, court=ca5, q=`Scroggins "City of Shreveport"`) — confirmed
   the Fifth Circuit opinion below: *Scroggins v. City of Shreveport*,
   No. 24-30777, filed 2025-10-17, status **Published**, no citation yet.
3. `read_document` (opinion_id=10705997, chunk 0) — the text stored under that
   opinion record is mismatched upstream: it is a 2022 W.D. Wash. minute order
   in an unrelated case (*Chang v. Vanderwielen*), not the Scroggins opinion.
   The claimed panel dissent therefore could not be verified; the petition's
   own description was used, discounted accordingly in `reasoning.md`.

No web searches. Both CourtListener lookups predate the snapshot and concern
the decision below, not this petition's disposition (forward mode; no outcome
exists).
