# Retrieval log — claude-judge, run 20261002T200745Z

- No `fedcourts query` / `open-events` corpus lookups.
- No CourtListener MCP calls.
- No web searches.
- Read the committed `metrics/statpack.md`, section "The interim docket (applications)", only to check the three candidates' stated 31/296 anchor against the per-Term rows (Term 2025: 17/226; Term 2024: 14/70; earlier eligible Terms unparsed). Local file read, no ranged-corpus transfer.
- Read the provisioned record: `event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-10-02.json`, `record/documents/documents.json` and the now-OCR'd `record/documents/application.txt`, and each `record/blinded/<alias>/` directory (prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md, retrieval_log.json). No `record/opinion/` slot exists on this interim cell, as expected.

Nothing beyond the provisioned inputs and the committed statpack was consulted.
