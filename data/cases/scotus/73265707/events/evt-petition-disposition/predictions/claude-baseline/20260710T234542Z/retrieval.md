# Retrieval log — claude-baseline / 20260710T234542Z

Beyond the provisioned inputs (snapshot, petition text, event definition,
context), I consulted:

## Committed base rates

- `metrics/statpack.md` — overall and SCOTUS-court base rates (resolved SCOTUS:
  other 78.4%, dismissed 15.9%, denied 4.4%, granted 1.4%). The
  "Modern discretionary-cert petitions by disposition" section named in the
  predict prompt is not present in the committed statpack (see `flags.json`).

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "596 U.S. 411" --citation "465 U.S. 1" --citation "537 U.S. 79" --corpus-backend ranged`
   — no matching priors returned.
   - `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --corpus-backend ranged`
   — recent resolved SCOTUS priors; the June 2026 conference cohort is
   overwhelmingly `denied` (e.g. 25-24, 25-1220, 25-1222), with rare grants.
   - `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --disposition dismissed --corpus-backend ranged`
   — the three 2020s `dismissed` priors (25-34, 25-46, 25-39) are counseled,
   paid cases (Rule 46 settlement dismissals), not the IFP-denied/non-payment
   pattern, informing the denied-vs-dismissed categorical call.
   - `ranged corpus reads: 205 GET(s), 53739520 byte(s)`

## CourtListener MCP

None. The provisioned snapshot was fetched today (2026-07-10) and already
contains the dispositive post-conference IFP-denial order, so no live docket
or opinion lookups were needed.

## Web searches

None.
