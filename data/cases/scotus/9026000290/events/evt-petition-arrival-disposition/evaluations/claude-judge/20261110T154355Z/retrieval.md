# Evaluator retrieval log

- I read the provisioned inputs only: the event, outcome, context, the 2026-11-09 snapshot, the QPs, and the blinded candidates' prediction, reasoning, forecast, retrieval.md and retrieval_log.json.
- I ran `uv run fedcourts statpack-at data/cases/scotus/9026000290/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for codex-baseline, gemini-baseline and claude-baseline. All three resolved to build 2420d5dd72e1 (digest sha256:e9eca3b0…). In that build, the sal-v4 `baseline` prefix (reached) rate pooled over OT2017–2025 is 638/12,720. I used this only to check the candidates' anchor arithmetic.
- No `fedcourts query`, no CourtListener MCP calls and no web searches.
