# Retrieval log — scotus/73281694 evt-petition-disposition (claude-baseline, 20260717T072907Z)

Beyond the provisioned inputs (snapshot, questions-presented, petition, brief
in opposition, event definition, context.json), I consulted:

## Corpus base rates (committed statpack)

- Read `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", per-Term cert table (Term 2025 est. grant rate 2.5%), relist
  and CVSG signal cuts. This statpack build carries no "Segment base rate by
  salience band" table, so I anchored on the modern-cert and per-Term tables
  plus the CVSG/relist cuts.

## Corpus lookups (`fedcourts query`, ranged reads against the remote corpus)

1. `uv run fedcourts query --court scotus --citation "600 U.S. 122" --era 2020s`
   → no rows returned.
   `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --topic "personal jurisdiction" --era 2020s`
   → no rows returned.
   `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --citation "486 U.S. 888" --citation "262 U.S. 312" --era 2020s`
   → no rows returned.
   `ranged corpus reads: 420 GET(s), 110100480 byte(s)`

No similar resolved priors surfaced from the corpus for these filters, so the
quantitative anchor is the statpack alone.

## CourtListener MCP

Not used. The provisioned record (full docket through July 15, 2026, plus
petition, BIO with appended trial-court orders, and questions presented) was
sufficient; the disposition will not occur before the September 28, 2026
conference, so no fresher docket state was needed.

## Web searches

None.
