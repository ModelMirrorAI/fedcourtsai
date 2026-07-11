# Retrieval log — claude-baseline / 20260710T234542Z

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "Strickland v. Washington" --citation "Brecht v. Abramson" --corpus-backend ranged --limit 8`
  → no rows. `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
- `uv run fedcourts query --court scotus --citation "466 U.S. 668" --citation "507 U.S. 619" --corpus-backend ranged --limit 8`
  → no rows. `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
- `uv run fedcourts query --court scotus --era 2020s --corpus-backend ranged --limit 10`
  → 10 resolved 2020s-era SCOTUS priors (9 denied, 1 granted — the granted
  one counseled and high-profile). `ranged corpus reads: 378 GET(s), 99090432 byte(s)`

## Base rates

- Read the committed `metrics/statpack.md`: overall resolved base rate,
  the SCOTUS by-court cut (granted 1.4% of resolved), and the by-Term table.
  The "Modern discretionary-cert petitions by disposition" section the
  prompt points to is not present in the committed statpack (flagged).

## CourtListener MCP

- Attempted two docket searches (CA8 No. 25-1965; Nebraska "Price v.
  Lewien") to confirm lower-court posture. Both failed with
  `REDIS_URL is not set; cannot access session store.` — the server was
  down for this cell; no CourtListener data informed the prediction.

## Web

- None.
