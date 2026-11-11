# Evaluator Retrieval Log (`scotus/9026000314` — `evt-petition-disposition`)

- Read `.github/prompts/evaluate.md` and schemas (`schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`).
- Read provisioned event and case record files under `data/cases/scotus/9026000314/`:
  - `events/evt-petition-disposition/event.yaml`
  - `events/evt-petition-disposition/outcome.json`
  - `record/context.json`
  - `record/snapshots/2026-11-09.json`
  - `record/documents/documents.json`, `questions-presented.txt`, `appendix.txt`, `petition.txt`
  - `record/blinded/candidate-{a,b,c}/{prediction.json,reasoning.md,predicted_reasoning.md,retrieval.md,retrieval_log.json}`
- Read `metrics/statpack.md` and ran `uv run fedcourts statpack-at data/cases/scotus/9026000314/record/blinded/candidate-{a,b,c}/ --ref origin/main --out-dir /tmp/statpack-at/candidate-{a,b,c}` to reconstruct the committed statpack (`886549a3ac32bdba039691b6d2ca7dc57bb72561`) as of the candidates' prediction run (`20261015T142602Z`) and verify their `sal-v4` `baseline` risk-set base-rate citations.
- No external CourtListener MCP or web searches were needed because the outcome was a summary denial of certiorari with no opinion and the provisioned appendix contained the full text of the D.C. Circuit orders below.
