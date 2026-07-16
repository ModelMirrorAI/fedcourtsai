# Retrieval log — scotus/73280380 / evt-petition-disposition / claude-baseline / 20260716T205846Z

Beyond the provisioned inputs (snapshot, questions-presented, petition, BIO,
`record/context.json`), I consulted:

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert disposition split, CA9
  originating-circuit cut, relist-count cut, CVSG cut, per-Term grant rates.
  (Committed file; no corpus reads.)

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "549 U.S. 1" --citation "496 U.S. 384" --limit 5`
   → 0 rows returned.
   `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
2. `uv run fedcourts query --court scotus --citation "496 U.S. 384" --limit 5`
   → 0 rows returned.
   `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
3. `uv run fedcourts query --court scotus --citation "549 U.S. 1" --limit 5`
   → 0 rows returned.
   `ranged corpus reads: 418 GET(s), 109576192 byte(s)`

No similar resolved priors surfaced for the Purcell / Cooter & Gell citation
filters, so the prediction anchors on the statpack base rates plus the
case-specific docket signals.

## CourtListener MCP

None — the provisioned snapshot is dated today (2026-07-16) and already
carries the full docket history through the 9/28/2026 long-conference
distribution, so live retrieval offered no marginal value. The
conditional-grant-rate context for called-for responses cited in
`reasoning.md` is general background knowledge, not a retrieved source.

## Web searches

None.
