# Retrieval log

## Corpus (`fedcourts query`, read-only via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --limit 12`
   stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   Returned mostly 26A-series application dockets plus three paid cert dockets (25-1131 granted at 2 distributions, 25-1349 granted at 1, 26-426 granted); not comparable to a capital habeas petition and not used for the number.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 12`
   stderr: `ranged corpus reads: 11 GET(s), 2818048 byte(s)`
   Same shape; recorded for the transfer line.

## Base rates

- `metrics/statpack.md`: Modern discretionary-cert petitions by disposition; by originating circuit (ca11 row); relist count, CVSG status and capital-case marking cuts (paid scored segment); SCOTUS cert petitions by Term; Segment base rate by salience band (sal-v4), pooling the `baseline` bracketed `reached` figures for OT2017 through OT2024.

## CourtListener MCP

1. `search` type=d, q="White v. Plappert", court=scotus — 0 results.
2. `search` type=o, court=ca11, filed_after=2024-10-01, q="Davis v. Commissioner Alabama Department of Corrections Strickland prejudice jury hesitation" — confirmed Jimmy Davis, Jr. v. Commissioner, 120 F.4th 768 (CA11 Oct. 30, 2024), status Published, docket 18-14671; two further Published entries dated 2026-02-19 (the rehearing-denial opinions).
3. `search` type=d, q="Plappert", filed_after=2025-01-01 — 53 results, all W.D. Ky. habeas dockets; no Supreme Court docket surfaced.

No web searches. No retrieval touched this case's own Supreme Court docket beyond the provisioned snapshot; the petition is undecided (Conference of October 9, 2026).
