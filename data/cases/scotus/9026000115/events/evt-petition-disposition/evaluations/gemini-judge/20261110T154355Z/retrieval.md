# Evaluator Retrieval Log

No external corpus lookups (`fedcourts query` / `open-events`) or CourtListener MCP queries were performed.

Local verification performed beyond the provisioned case record (`event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-11-09.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, and `record/blinded/candidate-{a,b,c}/*`):

- Reconstructed the statpack build in force when the candidates ran (`run_id = 20261018T142134Z`) using `uv run fedcourts statpack-at data/cases/scotus/9026000115/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` (commit `886549a3ac32`, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`) to verify the candidates' `sal-v4` base-rate anchoring against the statpack build they saw.
