# Retrieval log (claude-judge)

- Read provisioned inputs only: event.yaml, outcome.json, record/context.json, record/snapshots/2026-11-09.json (ProceedingsandOrder), the head of record/documents/brief-in-opposition.txt (plus a grep for vehicle terms), and record/blinded/candidate-{a,b,c}/ (prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md, retrieval_log.json).
- `uv run fedcourts statpack-at data/cases/scotus/9026000107/record/blinded/candidate-{a,b,c}/ --ref origin/main --out-dir /tmp/statpack-at/candidate-{a,b,c}`: all three resolved to build 7bcde3b105cb (digest sha256:84feb679…, landed 2026-10-28; alternative_sha null). Read the sal-v4 segment-base-rate table from /tmp/statpack-at/gemini-baseline/statpack.md.
- No `fedcourts query`, no CourtListener MCP, and no web searches.
