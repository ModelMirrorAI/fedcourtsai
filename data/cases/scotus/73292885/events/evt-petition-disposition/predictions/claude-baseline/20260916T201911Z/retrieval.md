# Retrieval log

## Corpus (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 73292885 --event evt-petition-disposition --role predictor` — path resolution only.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   Returned recent granted rows (mostly OT2025 substantive applications and counseled Second Amendment petitions); no subject filter is available, so used as a shape check only.
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 6`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned six September 2026 denials at distribution count 0; shape check only.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "Petitions by originating court", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (pooled `baseline` bracketed `reached` over OT2017–OT2024).

## CourtListener MCP

1. `search` (type `o`, q `Pestarino`, courts `wash`, `washctapp`, 10 results) — 0 results. The Washington Court of Appeals decision is unpublished and appears not to be indexed.

## Web

No web searches.

Nothing was retrieved about this petition's own disposition; the September 28, 2026 conference postdates this run.
