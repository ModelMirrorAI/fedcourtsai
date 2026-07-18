# Retrieval log — scotus/73500233 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-07-18.json`,
`record/documents/petition.txt`, `record/documents/questions-presented.txt`,
`record/documents/documents.json`, `record/context.json`):

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   - stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
   - Purpose: profile recently granted petitions (distribution counts, salience,
     counsel, originating courts) against this case's signals.

## Base rates

- Committed `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "Cert petitions by relist count", "Cert petitions by CVSG
  status", "Petitions by originating court (incl. state courts)", and the
  per-Term table (paid/IFP filings, grant rates). No salience-band table is
  present in the committed statpack version, so the relist/CVSG cuts were used
  directly.

## CourtListener MCP

None. The provisioned snapshot was fetched the same day as this run
(2026-07-18) and already reflects the docket through the June 24, 2026
distribution entry, so no live docket lookup was needed.

## Web searches

None.
