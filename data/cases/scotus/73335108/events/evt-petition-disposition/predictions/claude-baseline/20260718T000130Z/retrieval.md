# Retrieval log — scotus/73335108, evt-petition-disposition, claude-baseline, 20260718T000130Z

Beyond the provisioned inputs (snapshot, questions-presented.txt, petition.txt,
context.json) I consulted:

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition",
  "Modern cert petitions by originating circuit", "Cert petitions by relist
  count", "Cert petitions by CVSG status", "SCOTUS cert petitions by Term".
- `metrics/statpack.json` — per-Term per-fee-class grant rates (paid ~5.4–8.0%,
  IFP ~0.9–1.1% across Terms 2023–2025).

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era modern --limit 8`
   → 0 rows.
   stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
2. `uv run fedcourts query --court scotus --limit 5`
   → 5 rows (era 2020s), but all with null captions — not usable for
   qualitative matching; no substantive weight in the prediction.
   stderr: `ranged corpus reads: 430 GET(s), 112590848 byte(s)`

## CourtListener MCP

None. The provisioned snapshot is dated 2026-07-17 (one day before the run),
the conference is not until 2026-09-28, and the petition text was fully
provisioned, so live docket retrieval had nothing to add.

## Web searches

None.
