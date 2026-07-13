# Retrieval log

Mode: `forward` (per `record/context.json`).

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition granted --limit 5 --corpus-backend ranged`
  — pulled recent granted SCOTUS priors for context on the granted-side
  population; none were on-point for a held three-judge-court direct appeal.
  Stderr: `ranged corpus reads: 129 GET(s), 33816576 byte(s)`
- Read the committed `metrics/statpack.md` for cert base rates (considered and
  largely discounted — this cell is a mandatory-jurisdiction appeal, not a
  discretionary cert petition; see `reasoning.md`).

## CourtListener

No CourtListener MCP or REST calls. The provisioned snapshot already contained
the disposition (see `flags.json`), so any further retrieval about this case
risked only deepening the leakage without improving the pre-decision analysis.

## Repo-internal reads (labeling convention, not case facts)

- `src/fedcourtsai/pipeline/cert_signals.py` and
  `src/fedcourtsai/pipeline/historical.py` — to confirm that GVR-style
  dispositions map to `granted` in this pipeline's vocabulary.

No web searches.
