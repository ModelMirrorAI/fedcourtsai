# Retrieval — claude-judge, scotus/73500232, evt-petition-disposition, run 20261007T150255Z

No retrieval beyond the provisioned inputs and the committed repository surfaces.

- Provisioned inputs read: `event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/documents.json`, `questions-presented.txt`, the head of `petition.txt`, and every file under `record/blinded/candidate-{a,b,c}/` (`prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`). No `record/opinion/` slot was staged (cert cell; none expected).
- Committed base-rate surface: `metrics/statpack.md`, "Segment base rate by salience band (sal-v4)" table, bracketed `reached` figures for the `baseline` band, Terms 2017–2024, pooled resolved-weighted by a local arithmetic script (≈593 / 11,580 = 0.0512). `config/tracking.yaml` read for `salience.base_rate_lookback_terms` (10).
- Corpus lookups (`fedcourts query` / `open-events`): none. No `ranged corpus reads` line to record.
- CourtListener MCP lookups: none.
- Web searches: none.
