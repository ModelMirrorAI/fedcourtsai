# Retrieval log (claude-judge, 20261110T154355Z)

- Read the provisioned inputs: the evaluate prompt, `schemas/evaluation.schema.json`, event.yaml, outcome.json, record/context.json, and each candidate's staged prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md and retrieval_log.json under record/blinded/.
- `uv run fedcourts statpack-at data/cases/scotus/9026000249/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` resolved to build 886549a3ac32 (landed 2026-10-13). I read its sal-v4 segment table to check gemini-baseline's anchor figure, which codex-baseline's and claude-baseline's figures also match.
- No `fedcourts query` or `open-events` calls, no CourtListener MCP lookups, no web searches.
