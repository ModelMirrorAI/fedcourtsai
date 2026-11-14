# Evaluator Retrieval Log

Provisioned and repository inputs read:

- `.github/prompts/evaluate.md`, `config/evaluators.yaml`, `schemas/evaluation.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`.
- Case and event artifacts under `data/cases/scotus/73280982/`: `events/evt-order-cvsg-disposition/event.yaml`, `events/evt-order-cvsg-disposition/outcome.json`, `record/context.json`, `record/snapshots/2026-11-14.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/sg-invited-brief.txt`, `record/documents/supplemental-brief.txt`, `summaries/2026-11-09.md`, and all staged candidate directories under `record/blinded/{claude-baseline,codex-baseline,gemini-baseline}/`.
- Base-rate artifacts: `metrics/statpack.md` and historical statpack build `73762050f49c` (`sha256:345aff2a4fcdad755e6606d092e6c2475966c0bd858d291155914ef722d88fe8`, landed `2026-09-14T08:42:59-04:00`), reconstructed into temporary scratch space outside the repository tree via `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/<alias>/ --ref origin/main --out-dir /home/runner/.gemini/tmp/fedcourtsai/statpack-at/<alias>` to verify each candidate's `sal-v4` and CVSG base-rate citations as of `20260918T174135Z`.

No `fedcourts query` or `fedcourts open-events` corpus lookups, no CourtListener MCP lookups, and no web searches were performed.
