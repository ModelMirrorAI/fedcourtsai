# Retrieval log — claude-judge, run 20261005T221055Z, cell scotus/73369988 / evt-petition-disposition

## Corpus lookups

None. No `fedcourts query` or `fedcourts open-events` was run, so no
`ranged corpus reads:` line was produced.

## CourtListener MCP lookups

None.

## Web searches

None.

## Local reads beyond the per-case record

- `metrics/statpack.md`, "Segment base rate by salience band (sal-v4)" table —
  the baseline band's bracketed `reached` figures for OT2017–OT2024, pooled
  resolved-weighted to 0.0512 (weighted n 11,580). The caption renders 10 of 10
  Terms, so the rendered window is the pack's window.
- `metrics/statpack.json` via the in-code pooler
  (`fedcourtsai.pipeline.base_rates.prediction_base_rate`, lookback 0 and 10),
  as a cross-check only: it returns 0.051209, agreeing with the rendered-table
  figure to four decimals. The recorded `segment_base_rate` is the rendered-table
  value.
- `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py` for the scoring
  definitions (`is_correct`, `brier_score`, `brier_skill`, `_pooled_band_rate`),
  `config/tracking.yaml` for `salience.base_rate_lookback_terms` (10), and the
  three output schemas.
- The per-case record only through `record/blinded/<alias>/`, `record/context.json`,
  `record/snapshots/2026-10-05.json`, `record/documents/`, `event.yaml`, and
  `outcome.json`. Nothing under `data/qp-topics/` was read.
