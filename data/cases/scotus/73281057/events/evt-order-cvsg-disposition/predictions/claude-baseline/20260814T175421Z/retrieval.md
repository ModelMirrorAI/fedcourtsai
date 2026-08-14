# Retrieval log

Beyond the provisioned inputs (snapshot, event definition, context,
`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`) and the
committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "585 U.S. 755" --citation "467 U.S. 986" --citation "576 U.S. 350" --limit 5`
   - stderr: `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`
   - stderr note: citations filter — 161 of 590020 rows in scope carry
     citation data. Returned no rows (coverage gap, not absence of
     precedent).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned five rows, mostly application dockets; nothing case-specific
     was used from them.

## CourtListener MCP

None.

## Web searches

None.
