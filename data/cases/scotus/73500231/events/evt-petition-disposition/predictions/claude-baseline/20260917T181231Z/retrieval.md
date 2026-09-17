# Retrieval log

## Provisioned inputs (read)

- `data/cases/scotus/73500231/record/snapshots/2026-09-17.json`
- `data/cases/scotus/73500231/record/context.json`
- `data/cases/scotus/73500231/record/documents/documents.json`,
  `questions-presented.txt`, `petition.txt`
- `data/cases/scotus/73500231/events/evt-petition-disposition/event.yaml`
- `metrics/statpack.md` — "Modern discretionary-cert petitions by
  disposition", "by originating circuit", "by relist count (paid scored
  segment)", "by CVSG status (paid scored segment)", "by salience band",
  "SCOTUS cert petitions by Term", and "Segment base rate by salience band
  (sal-v4)".

## Corpus lookups (`fedcourts query`, through the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   Returned recent denied rows; the top of the ranking was substantive
   applications (26A-numbered), which are kept by design, plus a run of pro se
   denials from late August 2026. Used only to confirm the shape of the recent
   denied population, not as case-specific priors.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 12`
   `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   Recent granted rows carried distribution counts of 2 to 22 on the cert
   dockets (the 26A rows are applications); none was a pro se, response-waived
   petition. Used as a check that the relist signal is doing real work in the
   granted population.
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 1`
   (field-list check only; transfer line not recorded separately from run 1's
   warm cache).

## CourtListener MCP lookups

Two calls were attempted and both failed with HTTP 429 (rate limit exceeded,
300/hour) before any result was returned:

1. `search` type `d`, court `scotus`, party_name `Drevaleva` — to list the
   petitioner's prior Supreme Court dockets and their terminations (priors, not
   this case's outcome).
2. `search` type `o`, q `Drevaleva`, courts `cadc, scotus, ca9, ca10, cafc` —
   to read the decision below and the earlier appellate history.

A retry after the throttle window is recorded below if it ran.

## Web searches

None.
