# Retrieval log — claude-baseline, scotus/73279966, evt-order-cvsg-disposition, 20260820T181919Z

Beyond the provisioned inputs (snapshot 2026-05-19, event.yaml,
record/context.json, and the provisioned petition / questions-presented /
brief-in-opposition texts) and the committed `metrics/statpack.md`:

## Corpus queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "596 U.S. 832" --limit 5`
   — attempted known-case lookup of United States v. Washington (2022) as a
   posture prior. Zero rows (sparse citation coverage, as the note warned).
   - `ranged corpus reads: 1335 GET(s), 349962240 byte(s)`
   - `note: citations filter: 159 of 590419 rows in scope (scotus) carry citation data ...`
2. `uv run fedcourts query --court scotus --disposition granted --limit 5`
   — recent granted SCOTUS priors for grant-posture context (distribution
   counts and salience scores of recent grants). Returned 5 rows.
   - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`

## CourtListener MCP lookups

1. `search` (type=d, court=scotus, case_name="Menocal") — looking for the
   related GEO Group v. Menocal SCOTUS docket. 0 results.
2. `search` (type=o, court=scotus, q="Menocal GEO Group") — found the opinion:
   GEO Group, Inc. v. Menocal, No. 24-758, decided 2026-02-25. Used only to
   confirm the companion case's decision date precedes this cell's snapshot
   (it informs the summary-disposition/GVR claim); a related case's public
   ruling, not this case's disposition.

## Web searches

None.

I did not retrieve this case's own current docket state, disposition, or any
post-snapshot filing in it.
