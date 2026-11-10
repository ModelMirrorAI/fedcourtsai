# Evaluator retrieval

- Read the evaluation contract and output schemas, the resolved event and outcome, every staged candidate's prediction and both prose documents, retrieval notes and harness-captured logs, the evaluator's context and November 9 docket snapshot, and the provisioned opposition and document manifest. No opinion or writing files were staged. These are provisioned inputs, not external retrieval.
- Read the committed `metrics/statpack.md` for aggregate context. Reconstructed the candidate-era aggregate build with these successful commands:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run --offline --no-sync fedcourts statpack-at data/cases/scotus/9026000055/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run --offline --no-sync fedcourts statpack-at data/cases/scotus/9026000055/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run --offline --no-sync fedcourts statpack-at data/cases/scotus/9026000055/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- All three resolved to build `886549a3ac32bdba039691b6d2ca7dc57bb72561`, landed October 13, 2026, digest `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, with no alternative build. Read the reconstructed relist and sal-v4 risk-set sections and checked the candidates' historical arithmetic. These commands consult only statpack history, not prediction history; no ranged-corpus transfer line was produced.
- No `fedcourts query` or `open-events`, CourtListener MCP lookups, web searches, external orders, opinions, or commentary were used. No candidate identity was sought.
