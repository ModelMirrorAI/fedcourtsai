# Retrieval log — scotus/73300246 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Mode: `forward` (retrieval unrestricted; nothing outcome-revealing exists yet —
the petition is distributed for the 2026-09-28 conference).

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   — stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`.
   Pulled recent granted priors for context; none topically close (the corpus
   carries no takings/nature-of-suit filter on SCOTUS rows), so this informed
   nothing beyond confirming the granted set skews toward split-bearing federal
   cases unlike this one.

## Base rates

- Committed `metrics/statpack.md`: modern discretionary-cert grant rate
  ~2.5–3.3% per recent Term; relist-0 bucket 0.8% granted; no-CVSG bucket 3.0%;
  paid vs IFP fee-class detail noted. (The prompt's "Segment base rate by
  salience band" table is not present in the committed statpack, so I anchored
  on the relist/CVSG cuts directly.)

## CourtListener MCP lookups

1. `search(type=o, court=scotus, q="takings clause \"just compensation\" access landlocked", filed_after=2019-01-01)` — 0 results.
2. `search(type=o, court=scotus, q="\"Takings Clause\" access easement", filed_after=2019-01-01)` — 5 results:
   Sheetz v. El Dorado County (2024), Knick v. Township of Scott (2019),
   Cedar Point Nursery v. Hassid (2021), PennEast Pipeline Co. v. New Jersey
   (2021). Used to confirm the Court's recent takings docket contains no
   pending or recent case on landlocked-access-by-government-sale (so no GVR
   source and no companion-case signal).

## Web searches

None.
