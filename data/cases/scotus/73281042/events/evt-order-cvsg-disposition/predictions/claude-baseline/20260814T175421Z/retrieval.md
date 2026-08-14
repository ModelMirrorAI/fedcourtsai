# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-14.json`, `event.yaml`,
`record/context.json`, and the provisioned document texts
`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`) and the
committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --citation "600 U.S. 570" --citation "530 U.S. 640" --citation "468 U.S. 609" --limit 6`
   - stderr: `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`
   - stderr note: `citations filter: 161 of 590020 rows in scope (scotus) carry citation data, and the column holds a case's OWN reporter cites (not a cases-citing-this-authority graph) — an empty result here usually means missing data, not no match`
   - Result: no rows returned (sparse-coverage gap, per the note). Not retried.

## CourtListener MCP lookups

None.

## Web searches

None.
