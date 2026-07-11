# Retrieval log — claude-baseline / 20260710T234542Z

Beyond the provisioned inputs (snapshot `2026-07-10.json`, `petition.txt`,
`questions-presented.txt`, `documents.json`, event definition, context):

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --corpus-backend ranged --limit 10`
  — stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
  — ten resolved 2020s SCOTUS priors used as a modern-disposition sample
  (nine denials incl. pro se state-civil analog Kama v. Greenridge Place
  Apartments, 25-1222; one grant, the counseled immigration case Montoya
  Palacios, 25-1223).

## Base rates

- Read the committed `metrics/statpack.md` (overall, by-court, by-Term
  tables). Note: the "Modern discretionary-cert petitions by disposition"
  section referenced in the predict prompt is not present in the committed
  statpack; I used the scotus by-court row (granted 1.4% of 296 resolved)
  and general knowledge of pro se cert grant rates instead (flagged in
  `flags.json`).

## CourtListener MCP

- None. The provisioned snapshot was fetched today (2026-07-10) from the
  Supreme Court docket and is current; no additional docket lookup was
  needed for this prediction.

## Web searches

- None.
