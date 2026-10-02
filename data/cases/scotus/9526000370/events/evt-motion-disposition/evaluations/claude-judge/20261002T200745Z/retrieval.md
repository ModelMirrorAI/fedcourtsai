# Retrieval log — claude-judge / 20261002T200745Z

No corpus lookup (`fedcourts query` / `open-events`), no CourtListener MCP call, and no web search was made. Beyond the provisioned cell inputs (`event.yaml`, `outcome.json`, `record/context.json`, `record/blinded/*`, `record/documents/`, `record/snapshots/2026-10-01.json`) I read only committed repository files:

- `metrics/statpack.md`, section *The interim docket (applications)* — to describe what the harness-stamped interim baseline should pool (Terms 2025 and 2024, 31/296), not to write a rate.
- `docs/salience.md`, *The interim docket* — the floor rule (`INTERIM_BASE_RATE_MIN_RESOLVED` = 50).
- `data/cases/scotus/9526000370/summaries/*.md` — the case's plain-language summaries, as post-decision context for the big-case read.
- `src/fedcourtsai/pipeline/evaluate.py` / `base_rates.py` — the `is_correct`, `brier_score` and `interim_base_rate` definitions, to match them.
- `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.

Nothing under `data/qp-topics/` was read; the committed `predictions/` and `evaluations/` trees for this event were not read.
