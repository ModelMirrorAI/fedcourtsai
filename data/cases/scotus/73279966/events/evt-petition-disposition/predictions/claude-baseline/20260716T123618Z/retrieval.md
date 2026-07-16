# Retrieval log — scotus/73279966 evt-petition-disposition (claude-baseline, 20260716T123618Z)

Mode: `forward` (retrieval unrestricted; nothing about this petition's own
disposition was sought — the CVSG response is still pending as of the
2026-07-16 snapshot, so no disposition exists).

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --citation "McCulloch v. Maryland" --citation "Kansas v. Garcia" --corpus-backend ranged`
  → 0 rows. stderr: `ranged corpus reads: 418 GET(s), 109510656 byte(s)`
- `uv run fedcourts query --court scotus --era 2020s --citation "Washington v. United States" --corpus-backend ranged`
  → 0 rows. stderr: `ranged corpus reads: 418 GET(s), 109510656 byte(s)`
- `uv run fedcourts query --court scotus --topic immigration --era 2020s --corpus-backend ranged`
  → 0 rows. stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`

No similar-prior rows matched these filters; priors context came from the
committed statpack instead.

## Base rates (committed statpack)

- `metrics/statpack.md` — modern discretionary-cert base rates, CVSG cut
  (granted 27.1% / denied 71.2%, n=59 resolved), relist cut, originating-circuit
  cut (ca9 modern slice: granted 3.0%).
- `metrics/statpack.json` — per-Term fee-class detail (Term 2025 paid: est.
  grant 5.4%; Term 2024 paid: 6.9%). The per-Term salience-band table named in
  the prompt is not present in this statpack build.

## CourtListener MCP

- `search(type=o, court=scotus, case_name="Menocal")` → confirmed
  *Geo Group, Inc. v. Menocal*, No. 24-758, decided 2026-02-25 (related GEO
  detainee litigation; forward signal on the Court's engagement, not this
  case's outcome).

## Web searches

None.
