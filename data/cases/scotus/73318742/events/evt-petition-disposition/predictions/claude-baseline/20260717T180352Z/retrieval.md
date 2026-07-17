# Retrieval log — scotus/73318742 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Beyond the provisioned inputs (snapshot, questions-presented, petition, BIO,
event definition, context.json):

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --limit 6`
   - stderr: `ranged corpus reads: 429 GET(s), 112328704 byte(s)`
   - Purpose: eyeball recent resolved SCOTUS cert priors around the same
     conference cycle. The relevance ranking surfaced mostly high-salience
     counseled petitions (Monsanto, Petersen, ATF cases) — useful as a contrast
     class (multiple distributions/relists before grant) but not close
     comparables to a pro se immunity petition, so I did not query further.

## Base rates

- Committed `metrics/statpack.md` — "Modern discretionary-cert petitions by
  disposition", relist-count, CVSG, originating-circuit, and per-Term tables.
- Committed `metrics/statpack.json` — per-fee-class (paid vs IFP) grant rates
  for Terms 2024–2025. (No salience-band table exists in this statpack build.)

## CourtListener MCP

None. The provisioned record was complete and current (snapshot fetched
2026-07-17, same day as this run), the petition and BIO texts were provided in
full, and the case is definitionally undecided (distributed for the 9/28/2026
conference), so live docket retrieval had nothing to add.

## Web searches

None.
