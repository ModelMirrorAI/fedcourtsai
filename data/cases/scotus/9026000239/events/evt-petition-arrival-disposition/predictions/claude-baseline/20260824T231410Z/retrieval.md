# Retrieval log

Beyond the provisioned inputs (event.yaml, snapshot 2026-08-24, context.json,
`record/documents/petition.txt` + `documents.json`) and the committed
`metrics/statpack.md`:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 8`
   — returned no rows (`modern` is not an era value; eras are decades).
   stderr: `ranged corpus reads: 752 GET(s), 196935680 byte(s)`
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   — 8 granted priors, but rows carried no captions/dates useful for analogy;
   not relied on beyond confirming the surface works.
   stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

## CourtListener MCP lookups

1. `search` (type `o`, q `"Proclamation 10888" asylum`) — 4 results,
   confirming the litigation chain below this petition: D.D.C. opinion
   2025-07-02 (No. 25-cv-306), D.C. Cir. partial-stay opinion 2025-08-01 and
   merits opinion 2026-04-24 (No. 25-5243). No disposition of this petition
   surfaced (it was docketed today, 2026-08-24).

## Web searches

None.
