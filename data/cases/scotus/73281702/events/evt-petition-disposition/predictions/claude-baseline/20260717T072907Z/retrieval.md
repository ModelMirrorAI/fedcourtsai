# Retrieval log — scotus/73281702 evt-petition-disposition (claude-baseline, 20260717T072907Z)

Mode: `forward` (pending petition; retrieval unrestricted). No search touched
this case's own disposition — none exists; the BIO is not due until
2026-07-24.

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --citation "Ramos v. Louisiana" --citation "Richardson v. United States"`
   — 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --citation "590 U.S. 83" --citation "526 U.S. 813"`
   — 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s`
   — generic 2020s priors (Monsanto, Petersen, McCoy, etc.); not topically
   relevant, used only as a sanity check on field shapes.
   stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`

Citation-filtered retrieval surfaced nothing for this topic, so priors came
from the committed base rates instead.

## Base rates

- `metrics/statpack.md` — modern discretionary-cert grant/deny split, relist
  and CVSG cuts, per-Term table.
- `metrics/statpack.json` — per-fee-class detail: Term 2025 paid petitions
  est. grant rate 5.36% (IFP 1.12%); Term 2024 paid 6.9%.
- Note: the "Segment base rate by salience band" table named in the predict
  prompt is not present in the committed statpack version.

## CourtListener MCP lookups

1. `search(type=d, court=scotus, q="continuous sexual abuse" unanimous)` — 0 results.
2. `search(type=o, court=scotus, q="continuous sexual abuse" unanimity)` — 4
   results (*Rivers v. Guerrero*, *Richardson v. United States*, *Cunningham
   v. California*); confirms the Court has no merits decision on
   course-of-conduct-statute unanimity post-*Ramos*.
3. `search(type=d, court=scotus, q="21.02" Texas)` — 0 results (CourtListener's
   SCOTUS docket full-text coverage is thin; companion-petition history taken
   from the petition's own account of *Allen* and *Purcell*).

## Web searches

None.
