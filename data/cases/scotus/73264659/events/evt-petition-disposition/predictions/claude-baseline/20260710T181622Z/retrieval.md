# Retrieval log — claude-baseline / 20260710T181622Z

Mode: `forward` (retrieval unrestricted; the outcome does not yet exist).

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --corpus-backend ranged`
  - stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
  - Returned ~20 resolved 2020s SCOTUS priors, including the same-week
    Term-2025 IFP docket series (25-7256, 25-7257, 25-7258, 25-7260 …
    25-7273): all denied at first conference. The single grant in the result
    set was a counseled paid-docket immigration case (25-1223).

## Base rates

- Committed `metrics/statpack.md`: overall SCOTUS resolved base rate
  (other 78.4%, dismissed 15.9%, denied 4.4%, granted 1.4% — blends
  merits-era labels). The "Modern discretionary-cert petitions by
  disposition" section the predict prompt points to is not present in the
  committed statpack (flagged in `flags.json`); the modern cert-stage
  grant/deny split was instead grounded in the `fedcourts query` priors above.

## CourtListener MCP

- None. The provisioned snapshot is dated today (2026-07-10) and shows the
  complete docket through distribution; the petition text and QPs were
  provisioned. Additional live retrieval would not have changed the analysis,
  so no MCP calls were spent.

## Web searches

- None.
