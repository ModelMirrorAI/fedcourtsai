# Retrieval log — scotus/73500241 / evt-petition-disposition / claude-baseline / 20260718T064904Z

## Corpus tooling

- Read the committed `metrics/statpack.md` and `metrics/statpack.json`
  (per-Term fee-class grant rates, relist/CVSG/originating-court cuts). The
  "Segment base rate by salience band" table named in the prompt is not
  present in either artifact, so I anchored on the paid-petition per-Term rate
  instead.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`. Used to
  profile what recent granted petitions look like (relist counts, counsel,
  originating courts) against this case's signals.

## CourtListener MCP

- `search(type=d, court=scotus, case_name="Asinor")` — 0 results.
- `search(type=d, court=scotus, q='"retention of property" OR "continued retention" seizure Fourth Amendment')` — 0 results.
- `search(type=d, court=scotus, case_name="Honda Lease")` — 0 results.

All three were checks for a pending/granted companion petition on the
Fourth-vs-Fifth Amendment retained-property split (which would make this a
hold/GVR candidate); CourtListener's SCOTUS docket coverage is sparse and none
surfaced. No information about this case's own disposition was sought or
encountered.

## Web searches

None.
