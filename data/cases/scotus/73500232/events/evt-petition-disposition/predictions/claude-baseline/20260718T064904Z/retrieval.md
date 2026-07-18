# Retrieval log — scotus/73500232 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-07-18.json`,
`record/documents/petition.txt`, `record/documents/questions-presented.txt`,
`record/documents/documents.json`, event definition, `record/context.json`):

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --era modern --limit 5`
   - stderr: `ranged corpus reads: 432 GET(s), 113246208 byte(s)`
   - Returned no rows (the era filter matched nothing on this slice).
2. `uv run fedcourts query --court scotus --limit 5`
   - stderr: `ranged corpus reads: 431 GET(s), 112984064 byte(s)`
   - Returned 5 recent SCOTUS rows ranked without topical similarity
     (no topic/judge/citation filter applies to this fact pattern); used
     only as a sanity check on the corpus surface, not as priors.

## Base rates

- Committed `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "Modern cert petitions by originating circuit" (ca3),
  "Cert petitions by relist count" (0-relist bucket), "Cert petitions by
  CVSG status", and the per-Term table. These anchored the probability.

## CourtListener MCP

- None. The provisioned snapshot was fetched today (2026-07-18) and already
  reflects the current docket (distributed 2026-07-15 for the 2026-09-28
  conference), so no live lookup was needed.

## Web searches

- None.
