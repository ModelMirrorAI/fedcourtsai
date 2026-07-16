# Retrieval log — scotus/73279493 / evt-petition-disposition / claude-baseline / 20260716T073449Z

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "523 U.S. 57" --limit 8`
   — 0 rows returned.
   `ranged corpus reads: 417 GET(s), 109117440 byte(s)`
2. `uv run fedcourts query --court scotus --topic bankruptcy --limit 8`
   — 0 rows returned.
   `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --citation "11 U.S.C." --limit 8`
   — 0 rows returned.
   `ranged corpus reads: 417 GET(s), 109117440 byte(s)`

No usable § 523(a)(6)/Geiger priors surfaced from the corpus.

## Base rates

- Read the committed `metrics/statpack.md` (modern discretionary-cert
  disposition table, originating-circuit, relist, CVSG, and per-Term
  sections) and the per-fee-class detail in `metrics/statpack.json`
  (paid vs. IFP grant rates by Term). This statpack build carries no
  salience-band table, so anchoring used the paid-fee-class and
  relist/CVSG cuts instead.

## CourtListener MCP

None. This forward cell's snapshot ends five months before the run date
(last entry Feb 2, 2026: response requested, due Mar 4, 2026), so a live
docket lookup would most likely have surfaced this case's own disposition,
which the contract forbids retrieving; I predicted from the provisioned
record instead (see `flags.json`).

## Web searches

None.
