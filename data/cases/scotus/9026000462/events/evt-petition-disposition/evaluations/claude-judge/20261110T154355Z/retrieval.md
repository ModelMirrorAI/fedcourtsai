# Evaluator retrieval log

- Provisioned inputs read: event.yaml, outcome.json, record/context.json, record/snapshots/2026-11-09.json (proceedings), record/documents/questions-presented.txt, and each candidate's blinded prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md and retrieval_log.json.
- `uv run fedcourts statpack-at data/cases/scotus/9026000462/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`: build 1c4f550b7b75 (landed 2026-09-28). I read its `sal-v4` segment-band table to check gemini-baseline's "~0.9%" anchor.
- No `fedcourts query`/`open-events` calls, no CourtListener MCP lookups, no web searches.
