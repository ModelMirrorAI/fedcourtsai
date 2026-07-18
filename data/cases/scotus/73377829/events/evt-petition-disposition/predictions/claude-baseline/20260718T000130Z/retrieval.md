# Retrieval log — scotus/73377829, run 20260718T000130Z

## Provisioned inputs

- `record/snapshots/2026-07-17.json` (docket snapshot, No. 25-1303)
- `record/documents/questions-presented.txt`
- `record/documents/petition.txt` (388 pp., truncated; read the QP, statement
  of the case, and Reasons I in full — the appendix bulk is what is truncated)
- `record/documents/documents.json`
- `events/evt-petition-disposition/event.yaml`, `record/context.json`
  (mode: forward)

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  → `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
  (recent granted-petition priors: distribution/relist counts, counsel profile)

## Base rates

- Committed `metrics/statpack.md` — "Modern discretionary-cert petitions by
  disposition", relist-count and CVSG cuts, originating-circuit cut, per-Term
  table (no salience-band section is present in the committed statpack).
- `metrics/statpack.json` — per-Term fee-class detail (Term 2025 paid grant
  rate ≈ 5.4%, Term 2024 ≈ 6.9%).

## CourtListener MCP

None — the provisioned snapshot (2026-07-17, one day old) and the petition
text covered the docket state; the case's own outcome was off-limits and does
not exist yet (BIO due 2026-08-14).

## Web searches

None.
