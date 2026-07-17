# Retrieval log — scotus/73281642 · evt-petition-disposition · claude-baseline · 20260717T000329Z

Beyond the provisioned inputs (snapshot 2026-07-16, questions-presented.txt,
petition.txt, brief-in-opposition.txt, documents.json), I consulted:

## Corpus tooling

- Committed base rates: `metrics/statpack.md` and `metrics/statpack.json`
  (modern discretionary-cert base rates; relist / CVSG / originating-circuit
  cuts; per-Term paid vs IFP fee-class grant rates). No salience-band section
  exists in the committed statpack.
- `uv run fedcourts query --court scotus --citation "594 U.S. 139" --citation
  "516 U.S. 442" --citation "568 U.S. 23" --limit 8`
  → 0 rows. stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
- `uv run fedcourts query --court scotus --citation "588 U.S. 180" --limit 5`
  → 0 rows. stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`

## CourtListener MCP

All three lookups aimed at predecessor/companion petitions in this doctrinal
line (forward-mode context predating the snapshot), not at this case's own
disposition. All returned zero results — CourtListener's RECAP/opinion indexes
do not cover SCOTUS cert dockets:

- `search(type=d, court=scotus, case_name="Slaybaugh")` → 0 results
- `search(type=d, court=scotus, docket_number="25-1163")` (companion *Pena*
  petition) → 0 results
- `search(type=o, court=scotus, q="Slaybaugh Rutherford")` → 0 results

## Web searches

None.

Predecessor-petition history therefore rests on the provisioned petition's own
citations (*Baker v. City of McKinney*, 145 S. Ct. 11 (2024) (Sotomayor, J.,
statement respecting denial)) and on training knowledge (*Lech* cert denial in
2020; *Slaybaugh* cert denial in 2025), as disclosed in `reasoning.md`.
