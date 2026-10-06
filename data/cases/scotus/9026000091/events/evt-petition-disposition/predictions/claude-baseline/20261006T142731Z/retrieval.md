# Retrieval log

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 9026000091 --event evt-petition-disposition --role predictor` (path resolution only; no corpus read).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7208960 byte(s)`
  Result: eight ranked rows, none on a CAFRA or fee-shifting question (mostly OT2025 interim applications and immigration grants). Not used for the forecast beyond confirming no close analogue in the corpus.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition"; "Cert petitions by relist count (paid scored segment)"; "Cert petitions by CVSG status (paid scored segment)"; "Cert petitions by salience band"; "SCOTUS cert petitions by Term"; "Segment base rate by salience band (sal-v4)" (pooled `baseline` reached rate over OT2017 to OT2025 = 5.0%, n = 12,720).

## CourtListener MCP

- `search` (type `o`, court `ca2`, q `"substantially prevails" CAFRA 2465 "prevailing party" Ross`, filed after 2025-11-01): **failed, HTTP 429 rate limit exceeded (1400/day)**.
- `search` (type `d`, court `scotus`, docket_number `19-659`): **failed, HTTP 429 rate limit exceeded (1400/day)**.
- No further calls attempted; no REST fallback by design.

## Web searches

None.
