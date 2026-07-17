# Retrieval log — scotus/73281632, evt-petition-disposition, claude-baseline, 20260717T000329Z

Mode: `forward` (`record/context.json`). Retrieval beyond the provisioned
inputs:

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "601 U.S. 416" --citation "594 U.S. 220" --citation "606 U.S. 656" --limit 6`
  - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
  - 0 rows returned (no resolved corpus priors matched those citations).
- `uv run fedcourts query --court scotus --citation "601 U.S. 416" --limit 5`
  - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
  - 0 rows returned.
- Base rates: read the committed `metrics/statpack.md` (modern
  discretionary-cert disposition table, originating-circuit, relist-count,
  CVSG, and per-Term tables). This statpack build has no salience-band
  section, so no band anchor was available.

## CourtListener MCP

- `search` (type=o): `FHFA "Appropriations Clause" funding 4516` — 4 results:
  the Ninth Circuit decision below (*Daisey Trust v. FHFA*, 2026-01-02),
  *Collins v. Treasury*, 83 F.4th 970 (5th Cir. 2023), and two entries for
  *CFPB v. CFSA*, 601 U.S. 416 (2024). Used to confirm no circuit split (both
  circuits to address FHFA funding rejected the challenge). No lookup of this
  case's own docket or disposition was made.

## Web searches

None.
