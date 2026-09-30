# Retrieval — claude-judge, scotus/9526000382 evt-motion-disposition, run 20260930T201759Z

No retrieval beyond the provisioned inputs and committed repository files.

- No `fedcourts query` / `open-events` calls (no `ranged corpus reads` lines to record).
- No CourtListener MCP lookups.
- No web searches or fetches.

Committed context read for scoring: `metrics/statpack.md`, section "The
interim docket (applications)", to check the candidates' pooled-baseline
claims (Terms 2024 and 2025 are the only parsed rows strictly before 2026:
31 granted over 296 resolved). The rate itself is the harness's on an interim
cell and was not written to any `evaluation.json`.

Per-case inputs read: `event.yaml`, `outcome.json`, `record/context.json`,
`record/snapshots/2026-09-30.json`, `record/documents/documents.json`, the
opening of `record/documents/application.txt`, and every file under
`record/blinded/candidate-{a,b,c}/`. No `record/opinion/` slot was staged,
as expected off the merits stage.
