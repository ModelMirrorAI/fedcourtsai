# Retrieval log

Beyond the provisioned inputs (snapshot, `questions-presented.txt`,
`petition.txt`, `documents.json`, `record/context.json`) and the committed
`metrics/statpack.md`:

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "549 U.S. 225"` — looking
  for Osborn v. Haley as a Westfall Act prior. Returned no rows; stderr:
  - `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  - `note: citations filter: 161 of 590339 rows in scope (scotus) carry citation data, and the column holds a case's OWN reporter cites (not a cases-citing-this-authority graph) — an empty result here usually means missing data, not no match`
  - Read as a coverage gap, not "no precedent"; not retried per the
    sparse-filter guidance.

## CourtListener MCP

1. `search` type=d, court=scotus, q="Carroll" — 0 results (RECAP carries no
   SCOTUS dockets).
2. `search` type=o, court=scotus, q='"Carroll" "Trump"' — 10 results, none a
   Trump/Carroll matter; confirms no SCOTUS opinion or noted writing exists on
   any related Carroll petition (this cell's own petition is three weeks old
   and undistributed, so no disposition of it could exist).
3. `search` type=o, court=ca2, citation="148 F.4th 110" — 0 results (citation
   not yet indexed).
4. `search` type=o, court=ca2, case_name="Carroll v. Trump", filed_after
   2025-01-01 — 4 results: No. 24-644 entries dated 2025-08-08 (the opinion the
   petition cites), 2025-09-08, and 2026-04-29 (the rehearing denial the
   petition cites), plus No. 23-793 (141 F.4th 366, 2025-06-13). Used to
   confirm the lower-court timeline stated in the petition; opinions not
   opened.

No web searches. This is a forward-mode cell; nothing outcome-revealing about
this petition was sought or surfaced.
