# Retrieval log — claude-judge, scotus/73278467 evt-brief-sg-disposition

- No corpus query, CourtListener MCP or web retrieval.
- Read the provisioned inputs: event.yaml, outcome.json, record/context.json, record/snapshots/2026-11-09.json (docket entries), summaries/2026-11-09.md, questions-presented.txt, and record/blinded/candidate-{a,b,c}/ (prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md, retrieval_log.json).
- `uv run fedcourts statpack-at data/cases/scotus/73278467/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` rebuilt build eb6830084a18 (landed 2026-10-19). I read its sal-v4 high-band rows to check the candidates' base-rate figures. It made no ranged corpus reads.
