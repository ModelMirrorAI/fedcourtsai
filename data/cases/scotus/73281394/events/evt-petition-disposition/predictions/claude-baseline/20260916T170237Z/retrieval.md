# Retrieval log — claude-baseline, scotus/73281394, evt-petition-disposition

Beyond the provisioned snapshot, context, and documents:

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  (default limit 20) — a broad sweep of recent granted SCOTUS rows to see the
  shape of the granted population (distribution counts, application forms).
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`. Nothing case-
  specific came of it; used only as context on relist counts among grants.

## Statpack

- `metrics/statpack.md` — "Modern discretionary-cert petitions by
  disposition", the relist-count and CVSG cuts (paid scored segment), "Cert
  petitions by salience band", "SCOTUS cert petitions by Term", and "Segment
  base rate by salience band (sal-v4)" (the `state` column, Terms 2017–2024,
  pooled on the bracketed `reached` denominators).

## CourtListener MCP lookups

1. `search` type `d`, court `scotus`, docket_number `25-1115` — 0 results (no
   RECAP docket for this matter).
2. `search` type `o`, court `scotus`, filed after 2024-01-01, query on juvenile
   life without parole / permanent incorrigibility / Jones v. Mississippi — 0
   results.
3. `search` type `r`, court `scotus`, filed after 2025-01-01, same subject
   terms — 0 results.

None of these surfaced any material about this case's disposition.

## Web fetch

- The State's reply brief (docket entry Aug 25 2026), fetched from the
  supremecourt.gov URL carried in the snapshot
  (`.../25-1115/420031/20260825135426029_25-1115%20Reply%20Brief.pdf`) and
  text-extracted locally. Read for the State's finality (Cox category 3),
  second-holding, split, and importance responses.
