# Retrieval log

Beyond the provisioned inputs (snapshot, `event.yaml`, `record/context.json`,
`record/documents/petition.txt`, `record/documents/questions-presented.txt`)
and the committed `metrics/statpack.md`:

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "602 U.S. 653"` — lookup
   of *Gonzalez v. Trevino* as a corpus prior. Returned no rows; the tool's
   note explains citation coverage is 159 of 590,483 SCOTUS rows in scope.
   Transfer line: `ranged corpus reads: 1343 GET(s), 352059392 byte(s)`.

## CourtListener MCP

2. `search` (opinions, court=ca8): `Murphy v. Schmitt retaliatory arrest` —
   confirmed *Mason Murphy v. Michael Schmitt*, published, filed 2025-07-09
   (the Eighth Circuit decision the petition claims a split with).
3. `search` (opinions, all courts): `Rahdar Friendswood` — zero results,
   consistent with the decision below being unpublished; no material about
   this case's disposition surfaced (none exists — the petition was docketed
   today).

No web searches.
