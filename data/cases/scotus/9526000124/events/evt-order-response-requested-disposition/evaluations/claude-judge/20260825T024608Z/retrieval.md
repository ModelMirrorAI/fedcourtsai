# Retrieval — claude-judge, 20260825T024608Z

Beyond the provisioned inputs (the event's `event.yaml` and `outcome.json`, the
three staged candidates under `record/blinded/`, and the schemas):

- `metrics/statpack.md`, "The interim docket (applications)" — read to verify the
  candidates' base-rate anchoring and to state what the harness-stamped interim
  baseline should support (Terms 2025 + 2024 pool: 30/225 ≈ 13.3%, clearing the
  50-resolution floor).
- `data/cases/scotus/9526000124/record/snapshots/2026-08-24.json` — the committed
  snapshot, read to verify two candidates' claim that the frozen
  `amicus_briefs: 6` undercounts: confirmed 6 "Brief amicus curiae" (singular) +
  7 "Brief amici curiae" (plural) = 13 amicus filings, and confirmed the Aug 24
  referral and grant entries. (The 2026-08-16 snapshot those candidates were
  provisioned is no longer committed; only 2026-08-24.json is.)

No `fedcourts query` / `open-events` corpus lookups (so no
`ranged corpus reads:` lines to record), no CourtListener MCP calls, and no web
searches.
