# Retrieval log

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  — recent granted SCOTUS petitions, for a feel of what the current Court's
  grants look like (relist counts, salience scores). Stderr transfer line:
  `ranged corpus reads: 26 GET(s), 6815744 byte(s)`.
- `uv run fedcourts corpus-info` — attempted for the freshness stamp; not
  runnable in this cell (no local blob; the ranged backend's remote URL is not
  in the shell environment). No corpus data returned.

I deliberately ran no query that filtered toward this case or its resolution,
and no returned row was this case's.

## CourtListener MCP

None. The provisioned filings (petition, brief in opposition, questions
presented), the docket snapshot, and the committed statpack covered what the
forecast needed; I avoided live retrieval that could surface this case's
post-snapshot history, since this forward cell runs ~10 months after its
frozen cutoff.

## Web searches

None.

## Committed repo inputs (beyond the provisioned cell inputs)

- `metrics/statpack.md` — modern-cert base rates, CVSG cut, relist cut,
  originating-circuit cut, and the sal-v3 segment-base-rate-by-salience-band
  table (pooled prior-Term high-band `reached` rate ≈40.9%, n=1074).
