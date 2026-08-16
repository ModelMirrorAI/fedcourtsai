# Retrieval log

Beyond the provisioned inputs (snapshot, `event.yaml`, `context.json`,
`petition.txt`, `questions-presented.txt`, `documents.json`) and the committed
`metrics/statpack.md`:

- CourtListener MCP `search` (type `o`, court `ca4`, q `Gasper EIDP`) — found
  the decision below: opinion 10750028, "David Gasper v. EIDP, Inc.",
  docket 24-1959, filed 2025-12-08, status "Published".
- CourtListener MCP `read_document` (opinion_id 10750028, chunk 0) — the text
  attached to that opinion record is a **different case** (a D. Or. opinion,
  *Northwest Investment Holdings, LLC v. PacWest Funding, Inc.*,
  3:24-cv-01144-HZ), so the decision below could not actually be read and its
  "Published" status is unverified. Noted in `flags.json`.

No `fedcourts query` / `open-events` corpus lookups were run (no `ranged
corpus reads` lines to record): the statpack's band, relist, and CVSG cuts
covered the priors this cell needed, and similar-case retrieval was unlikely
to move a number dominated by the pro se / waived-response posture.

No web searches.
