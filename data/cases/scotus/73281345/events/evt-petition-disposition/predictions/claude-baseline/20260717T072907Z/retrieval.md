# Retrieval log — scotus/73281345 / evt-petition-disposition / claude-baseline / 20260717T072907Z

Cell mode: `forward` (retrieval unrestricted; nothing about this case's own
disposition was sought or surfaced — the petition is pending, BIO filed
2026-07-13).

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  (~3% granted of resolved), relist and CVSG cuts, per-Term table.
- `metrics/statpack.json` — per-Term fee-class detail: paid grant rate Term
  2025 ≈ 5.4%, Term 2024 ≈ 6.9%, Term 2023 ≈ 8.0%. Note: the "Segment base
  rate by salience band" table the prompt references is not present in this
  statpack build (noted in `tooling.json`).

## Corpus lookups (`fedcourts query`, ranged backend)

- `uv run fedcourts query --court scotus --citation "514 U.S. 549" --limit 8`
  → 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
- `uv run fedcourts query --court scotus --limit 5` → 5 rows (2020s scotus
  priors, no captions/topics — uninformative for this QP).
  stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`

## CourtListener MCP lookups

- `search` (dockets, scotus, case_name="Chavarria", filed_after=2025-06-01)
  → 0 results: no cert petition filed in United States v. Chavarria (10th
  Cir. 2025), the petition's lead split case.
- `search` (dockets, scotus, case_name="Bryan v. United States",
  filed_after=2025-06-01) → 0 results: no companion petition from the
  Eleventh Circuit's Bryan either.

Both checks predate any disposition of this petition and concern related
litigation only (legitimate forward signal: no percolating companion cluster).

## Web searches

None.
