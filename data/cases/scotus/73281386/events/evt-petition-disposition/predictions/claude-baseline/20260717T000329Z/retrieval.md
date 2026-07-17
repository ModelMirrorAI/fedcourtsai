# Retrieval log — scotus/73281386 / evt-petition-disposition / claude-baseline / 20260717T000329Z

Mode: `forward` (pending petition; distributed for the 2026-09-28 conference).

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --citation "542 U.S. 367" --limit 8`
   — zero rows returned (no corpus priors indexed as citing *Cheney*).
   stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   — 8 recent resolved priors (2026-06-30 conference outcomes) used as
   qualitative context on grant/deny patterns among distributed petitions.
   stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`

## Base rates

- Committed `metrics/statpack.md`: modern discretionary-cert base rate
  (granted ≈ 3% of resolved), originating-circuit cut (cadc ≈ 11.8% granted,
  denial-reweighted), relist-count and CVSG cuts, and the per-Term table
  (Term 2025: est. grant rate 2.5%). This statpack version has no
  salience-band table, so no band anchor was available.

## CourtListener MCP

- Not used. The provisioned snapshot (2026-07-16, one day old) and full
  petition/BIO texts covered the record; no live lookups were needed, and no
  search touching this case's own (nonexistent) disposition was run.

## Web searches

- None.
