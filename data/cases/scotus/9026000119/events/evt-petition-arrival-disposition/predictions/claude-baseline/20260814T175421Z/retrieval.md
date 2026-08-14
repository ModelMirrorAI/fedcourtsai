# Retrieval log

Beyond the provisioned inputs (event.yaml, context.json, the 2026-08-14
snapshot, `record/documents/` petition and questions-presented text) and the
committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --citation "549 U.S. 483"` — a
   known-case lookup for Limtiaco v. Camacho, the most recent plenary grant on
   certiorari to the Supreme Court of Guam, sought as a comparable prior.
   **Zero rows returned.** stderr:
   - `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`
   - `note: citations filter: 161 of 590020 rows in scope (scotus) carry
     citation data, and the column holds a case's OWN reporter cites (not a
     cases-citing-this-authority graph) — an empty result here usually means
     missing data, not no match`

## CourtListener MCP lookups

2. `search` (opinions, court `gu`, query `Ybanez disqualification "Attorney
   General"`) — rejected client-side: invalid court id (`gu`; the correct id
   is `guam`). No request served.
3. `search` (opinions, court `guam`, query `Ybanez disqualification "Attorney
   General"`) — **0 results.** The Guam Supreme Court orders below are
   unreported and not on CourtListener; the petition's appendix descriptions
   are the only account of them used.

## Web searches

None.
