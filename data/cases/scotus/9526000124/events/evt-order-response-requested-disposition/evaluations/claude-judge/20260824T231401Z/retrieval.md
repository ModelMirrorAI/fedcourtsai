# Retrieval — claude-judge — 20260824T231401Z

No corpus queries (`fedcourts query` / `open-events`), no CourtListener MCP
lookups, and no web searches were run for this evaluation. Everything used is
committed in the repository:

- The provisioned cell inputs: `event.yaml`, `outcome.json`, and the three
  blinded candidate directories under `record/blinded/` (prediction, both
  prose documents, `retrieval.md`, `retrieval_log.json` for each).
- `data/cases/scotus/9526000124/record/snapshots/2026-08-24.json` — read to
  verify the realized order's terms (unqualified stay, referral and grant
  both entered 2026-08-24, per curiam with dissents from Justices Sotomayor,
  Kagan, and Jackson) and to verify the amicus-counter discrepancy two
  candidates reported: the docket carries 13 amicus filings before
  disposition, of which exactly 6 use the singular "Brief amicus curiae"
  caption — matching the frozen and outcome counts of 6.
- `metrics/statpack.md`, "The interim docket (applications)" — to state what
  the harness-stamped baseline should pool (Terms 2025 + 2024: 225 resolved
  substantive applications, 30 granted, ≈ 13.3%, clearing the 50-resolution
  floor).
