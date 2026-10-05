# Retrieval log

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 6`
  stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
  Returned six recent SCOTUS rows (stay applications and unrelated cert petitions); not topically similar, used only to confirm the priors surface.

## Base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (pooled `baseline` bracketed `reached` figures over OT2017–OT2025).

## CourtListener MCP lookups

- `search(type=o, q='Goodley "Supreme Rice"', court=ca5)` → 0 results.
- `search(type=d, docket_number=25-30509, court=ca5)` → 0 results.

## Web searches

None.
