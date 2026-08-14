# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-14.json`, `event.yaml`,
`record/context.json`, `record/documents/questions-presented.txt`,
`record/documents/petition.txt`, `documents.json`) and the committed
`metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --citation "549 U.S. 225" --citation "515 U.S. 417"`
  (the petition's controlling Westfall Act precedents, Osborn v. Haley and
  Gutierrez de Martinez v. Lamagno — a known-case lookup for prior rows).
  Returned **no rows**; stderr:
  - `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`
  - `note: citations filter: 161 of 590020 rows in scope (scotus) carry citation data, and the column holds a case's OWN reporter cites (not a cases-citing-this-authority graph) — an empty result here usually means missing data, not no match`

## CourtListener MCP

None. The provisioned petition already carried the procedural history
(including the related No. 25-573 denial) that outside lookups would have
supplied, and the cell's forward-mode question turns on the statpack anchor
plus the petition itself.

## Web searches

None.
