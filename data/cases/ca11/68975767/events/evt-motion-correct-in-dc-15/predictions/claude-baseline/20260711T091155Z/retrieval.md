# Retrieval log — ca11/68975767 / evt-motion-correct-in-dc-15 / claude-baseline / 20260711T091155Z

Beyond the provisioned inputs (snapshot, event definition, `record/context.json`),
I consulted:

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court ca11 --topic "motion to correct" --limit 5`
   — no rows returned.
   - `ranged corpus reads: 3 GET(s), 786432 byte(s)`
2. `uv run fedcourts query --court ca11 --limit 5`
   — returned 5 resolved ca11 priors, none analogous to a misdirected pro se
   "motion to correct" (older merits-era cases); not relied on.
   - `ranged corpus reads: 45 GET(s), 11796480 byte(s)`

## Base rates

- Committed `metrics/statpack.md` — "Cases by court" row for ca11
  (resolved: other 95.6%, denied 2.2%, granted 2.2%; n=45).

## CourtListener MCP

None — the provisioned snapshot contained the full docket context needed, and
retrieving this case's subsequent history is off-limits.

## Web searches

None.
