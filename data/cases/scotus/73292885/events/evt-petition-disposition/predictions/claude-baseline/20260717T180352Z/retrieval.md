# Retrieval log — scotus/73292885 evt-petition-disposition (claude-baseline, 20260717T180352Z)

Forward-mode cell; retrieval beyond the provisioned inputs was modest.

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  (overall grant ≈ 3%), "Cert petitions by relist count" (0-relist bucket:
  granted 0.8%), "Cert petitions by CVSG status" (none: granted 3.0%),
  "Petitions by originating court (incl. state courts)", and the per-Term
  table (Term 2025: est. grant rate 2.5%). This statpack build carries no
  "Segment base rate by salience band" section, so I anchored on the
  relist-count cut instead.

## Corpus lookups (`fedcourts` CLI)

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  — stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`.
  Context on what the modern Court actually grants: the returned priors include
  represented Second Amendment vehicles (Viramontes v. Cook County; Grant v.
  Higgins) — institutional parties and developed records, unlike this pro se
  domestic-relations petition.

## CourtListener MCP lookups

- `search(type="d", q="Pestarino")` — confirmed the petitioner's related
  federal case cited in the petition itself, Pestarino v. Pestarino, D. Nev.
  No. 3:25-cv-00082 (filed Feb. 11, 2025), a prior pro se federal collateral
  attack on the same state protection-order dispute. No search for this
  petition's own disposition was made (none exists; the conference is
  2026-09-28, in the future).

## Web searches

None.
