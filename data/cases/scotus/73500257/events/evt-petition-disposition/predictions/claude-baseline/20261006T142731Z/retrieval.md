# Retrieval log

## Corpus (`fedcourts query`, read-only via the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "595 U.S. 1" --citation "571 U.S. 3" --citation "595 U.S. 9" --citation "584 U.S. 100" --citation "575 U.S. 600"`
   - stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: no rows; the tool's `note:` line says only 200 SCOTUS rows carry any reporter citation, so the filter is a coverage gap rather than "no such case". Not used.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s` (first 12 rows)
   - stderr: `ranged corpus reads: 45 GET(s), 11665408 byte(s)`
   - Result: recent granted rows, dominated by substantive applications and federal-party petitions; none comparable to a municipal qualified-immunity petition. Not used beyond confirming the corpus holds few recent plenary-grant priors of this kind.
3. `uv run fedcourts query --court scotus --disposition summary-reversal`
   - stderr: `ranged corpus reads: 737 GET(s), 193069056 byte(s)`
   - Result: no rows. The corpus records no `summary-reversal` disposition label, so this label is not a usable prior surface; noted in `tooling.json`.

## Base rates

- `metrics/statpack.md`: *Modern discretionary-cert petitions by disposition*; *Cert petitions by relist count (paid scored segment)*; *by CVSG status (paid scored segment)*; *Cert petitions by salience band*; *SCOTUS cert petitions by Term*; *Segment base rate by salience band (sal-v4)* — pooled `baseline` bracketed `reached` rates over OT2017–OT2024 (5.1%, n ≈ 11,580).

## CourtListener MCP

- `search` (opinions, ca9): `"North Las Vegas" Salkoff "hot pursuit"` — **HTTP 429**, rate limit exceeded (1400/day), reset in ~3716 s. Not retried.
- `search` (opinions, scotus, filed after 2025-06-01): `"qualified immunity" "clearly established" "per curiam" reversed` — **HTTP 429**, same throttle. Not retried.

No results were obtained from CourtListener; the forecast rests on the provisioned snapshot, the three provisioned documents, and the statpack. No web searches.
