# Retrieval log — scotus/73372500, evt-petition-disposition, claude-baseline, 20260718T000130Z

Beyond the provisioned inputs (snapshot, petition.txt, questions-presented.txt,
documents.json, context.json) and the committed `metrics/statpack.md` /
`metrics/statpack.json`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   - stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
   - Purpose: recent resolved SCOTUS priors to calibrate docket-signal patterns
     (distribution/relist counts on grants vs. denials). Observed: the granted
     priors in the sample carried 3-22 distributions; single-distribution
     petitions in the sample were denied or dismissed.

## CourtListener MCP lookups

None. The provisioned snapshot (fetched 2026-07-17, the day before this run)
already carried the full current docket including the June 24 distribution
entry, and the respondents' waiver made a BIO fetch moot.

## Web searches

None.
