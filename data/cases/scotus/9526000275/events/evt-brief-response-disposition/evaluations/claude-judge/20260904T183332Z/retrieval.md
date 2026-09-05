# Retrieval — claude-judge — scotus/9526000275 / evt-brief-response-disposition — 20260904T183332Z

No corpus lookups (`fedcourts query` / `open-events` not run), no CourtListener
MCP lookups, and no web searches.

Consulted beyond the per-case provisioned inputs (`event.yaml`, `outcome.json`,
`record/context.json`, `record/snapshots/2026-09-04.json`,
`record/documents/documents.json`, and the two `record/blinded/<alias>/`
staging directories):

- `metrics/statpack.md`, *The interim docket* section — to check the
  strictly-prior pooled rate both candidates cite (Term 2025 17/226 + Term 2024
  14/70 = 31/296 ≈ 10.5%). Read for grading the base-rate use only; the stamped
  rate is the harness's.
- `src/fedcourtsai/pipeline/interim_signals.py` (`amicus_briefs` docstring) — to
  confirm that the docket's Sep 3 "Amicus brief … submitted" entry is
  deliberately not counted, so the outcome's `amicus_briefs: 0` is the rule
  working rather than a data-quality gap to flag.
