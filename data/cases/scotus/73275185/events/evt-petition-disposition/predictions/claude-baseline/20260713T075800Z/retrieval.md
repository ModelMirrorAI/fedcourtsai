# Retrieval log — scotus/73275185 / evt-petition-disposition / claude-baseline / 20260713T075800Z

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "Allen v. Milligan" --limit 5`
   — sought priors citing the companion case; returned no rows.
   `ranged corpus reads: 408 GET(s), 106954752 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   — pulled modern granted-petition priors for the distribution/relist-to-grant
   pattern (all five showed multiple distributions before grant).
   `ranged corpus reads: 129 GET(s), 33816576 byte(s)`

## Base rates

- Read the committed `metrics/statpack.md` — "Modern discretionary-cert
  petitions by disposition" (~4.9% grant, 92.6% denied on the 2025 Term
  live/historical slice) as the anchor; relist/CVSG cuts were empty
  (`unknown` bucket only).

## CourtListener MCP / REST

- None. The cell is marked `forward`, but the provisioned snapshot revealed
  that this case was actually decided on May 11, 2026 (see `flags.json`).
  Once that was apparent, any retrieval about this case risked pulling
  further outcome material (its disposition, subsequent history, coverage),
  which the contract forbids regardless of mode — so I made no MCP or REST
  calls and predicted from the provisioned inputs, the statpack, and the two
  corpus-prior lookups above.

## Web searches

- None.
