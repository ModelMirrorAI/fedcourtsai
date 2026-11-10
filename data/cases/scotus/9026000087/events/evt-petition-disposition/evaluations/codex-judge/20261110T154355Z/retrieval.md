# Evaluator retrieval

Read the provisioned evaluation contract and schemas, event and outcome, all three blinded candidates' prediction/prose/retrieval documents and harness logs, the decided snapshot and context, and relevant staged questions, opposition and appendix passages. Consulted local schema-model definitions for validation. No new case facts, external case documents, CourtListener lookups or web searches were retrieved. No corpus query or open-events lookup was performed, so there are no ranged-corpus transfer lines.

Historical-statpack checks, restricted to statpack history and with dependency syncing disabled:

- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000087/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` — succeeded; build `a14b36a1e190a86d6a01df2ce410f5f9e54fb98b`, digest `sha256:84a5c25d4bf0a2a70ba5c6e9392e2e21d43ed5b794de0ae59c27cf1973ad0e7e`, no alternative build.
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000087/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` — succeeded; build `0918fb18e74fb89adc9a0882411996400986925e`, digest `sha256:63295af7c6e50f69b51af1f372c8a86dd6e8a398f9e6bc408c56fd8af8ccaf4d`, no alternative build.
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000087/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` — succeeded; same build and digest as claude-baseline, no alternative build.

Inspected the reconstructed sal-v4 prior-Term reached table and terminal relist table only to assess each rationale's historical base-rate use. Did not compute an evaluator-owned segment base rate or inspect prediction history. These commands report no ranged-corpus transfer line.
