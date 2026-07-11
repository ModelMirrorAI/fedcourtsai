# Retrieval log

Beyond the provisioned inputs (event definition, snapshot
`record/snapshots/2026-07-11.json`, `record/context.json`), I consulted:

## Committed base rates

- `metrics/statpack.md` — overall and by-court base rates. The ca11 row has
  only 45 resolved cases and the roll-up is case-disposition-level
  (cert-heavy), so it provided no direct base rate for a procedural
  consolidation motion.

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court ca11 --topic "3840 Trademark" --corpus-backend ranged --limit 5`
   — returned no rows.
   - `ranged corpus reads: 99 GET(s), 25952256 byte(s)`
2. `uv run fedcourts query --court ca11 --corpus-backend ranged --limit 8`
   — returned 8 case-level priors (mostly disposition `other`); none were
   motion-level analogues, so they did not move the estimate.
   - `ranged corpus reads: 45 GET(s), 11796480 byte(s)`

## CourtListener MCP

None. The cell is `forward` mode, but the contract forbids retrieving this
case's own outcome, and any lookup of docket 23-12267 / companion appeal
23-13380 past 2023-11-01 would risk surfacing the actual ruling on this
motion. The provisioned snapshot already carried the post-filing docket
context I used.

## Web searches

None.
