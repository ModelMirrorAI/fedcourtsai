# Retrieval log — scotus/73286452 evt-petition-disposition (claude-baseline, 20260717T180352Z)

Beyond the provisioned inputs (snapshot `2026-07-17.json`,
`questions-presented.txt`, `petition.txt`, `documents.json`,
`record/context.json`):

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   - stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
   - Purpose: calibrate what recently granted petitions look like on
     observables (distribution counts of 3–22 before grant; counsel and
     amicus profiles).

## Committed base rates

2. `metrics/statpack.md` and `metrics/statpack.json` — modern
   discretionary-cert base rates; per-Term per-fee-class detail (paid
   Term-2025 est. grant rate ≈ 5.4%, IFP ≈ 1.1%); relist-count and CVSG
   cuts; originating-circuit cut (ca9 ≈ 3.0% granted). Note: the
   "Segment base rate by salience band" table described in the predict
   prompt is not present in the committed statpack.

## CourtListener MCP

3. `search` (type=o, court=scotus, q="Chiles v. Salazar conversion therapy
   licensed counselors speech", 3 results) — confirmed Chiles v. Salazar,
   No. 24-539, decided 2026-03-31 (cited throughout the petition; relevant
   to the GVR channel because the Ninth Circuit's rulings predate it).
   Nothing about this case's own disposition was sought or surfaced.

## Web searches

None.
