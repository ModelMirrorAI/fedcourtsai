# Retrieval — claude-judge, evt-brief-response-disposition, run 20260825T024608Z

No corpus queries (`fedcourts query` / `open-events`) were run, and no
CourtListener MCP lookups or web searches were made. Everything consulted was
committed in the repository:

- The event's `event.yaml` and `outcome.json`, and the three staged candidates
  under `record/blinded/` (prediction, both prose documents, `retrieval.md`,
  and the captured `retrieval_log.json` for each).
- `metrics/statpack.md`, "The interim docket (applications)" — to state in each
  `evaluation.md` what the harness-stamped baseline should rest on: OT2025
  (16/178) + OT2024 (14/47) = 30/225 ≈ 13.3%, clearing the 50-resolved floor.
  The rate itself is the harness's to stamp on an interim cell; none was
  written into any evaluation.
- `data/cases/scotus/9526000139/record/snapshots/2026-08-24.json` — a grep for
  amicus-filing styles ("amicus curiae" ×2, "amici curiae" ×3), to verify the
  amicus-counter undercount two candidates disclosed before flagging it.
