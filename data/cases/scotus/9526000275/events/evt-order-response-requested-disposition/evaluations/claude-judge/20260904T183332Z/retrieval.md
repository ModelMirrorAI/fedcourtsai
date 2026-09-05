# Retrieval log — claude-judge — scotus/9526000275 / evt-order-response-requested-disposition

Beyond the provisioned inputs (`event.yaml`, `outcome.json`, the two
`record/blinded/<alias>/` directories in full — `prediction.json`, `reasoning.md`,
`predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json` — the cell's own
`record/context.json`, the stored snapshot `record/snapshots/2026-09-04.json`,
`record/documents/documents.json`, and the three output schemas), I consulted:

- Committed `metrics/statpack.md`, section "The interim docket (applications)"
  (lines 203–230) — read for orientation on the harness-stamped baseline the
  interim rules describe; no rate was written from it.
- `record/documents/application.txt` — grep for the specific factual assertions
  in claude-baseline's `reasoning.md` (signature counts, Case No. 170595, the
  constructive-denial theory and its A.A.R.P. v. Trump citation, § 1257(a), the
  September 3 / September 4 deadlines), to check the rationale against the
  provisioned record.

No `fedcourts query` / `open-events` corpus lookups (so no `ranged corpus reads`
line to record), no CourtListener MCP lookups, and no web searches. Nothing
under `data/qp-topics/` was read, and nothing under the committed
`predictions/` tree.
