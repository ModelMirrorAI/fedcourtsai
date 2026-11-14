# Retrieval

- No corpus query, CourtListener MCP lookup or web search.
- `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` — rebuilt the statpack the candidates ran against (build `eb6830084a18`, landed 2026-10-19; no alternative build). All three candidates share one run id, so I used this build to check the base-rate figures each quoted (sal-v4 `high` band per-Term rows; paid-segment CVSG cut).
- Read the provisioned inputs only: the event and outcome, `record/context.json`, the 2026-11-14 docket snapshot, and each candidate's staged files and retrieval log.
