# Retrieval log — scotus/73281004 / evt-petition-disposition / claude-baseline / 20260716T205846Z

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition dismissed --limit 5 --corpus-backend ranged`
  - stderr: `ranged corpus reads: 233 GET(s), 61079552 byte(s)`
  - Purpose: shape-check recent dismissed-petition priors (all five: petitions
    short-circuited by waiver/withdrawal/settlement before merits action).

## Base rates

- Read the committed `metrics/statpack.md`: overall and modern
  discretionary-cert disposition base rates, relist-count cuts, CVSG cuts, and
  originating-circuit (ca9) cuts. (No salience-band table present in the
  committed statpack.)

## CourtListener MCP

- None. The provisioned snapshot (fetched 2026-07-16, same day as this run)
  already carried the dispositive docket entry — the June 30, 2026 joint
  motion to dismiss — so no live docket lookup was needed.

## Web searches

- None.
