# Evaluation retrieval

Read the provisioned event and outcome, resolved docket snapshot, context, questions presented, petition and appendix excerpts, document manifest, and all three blinded candidates' predictions, rationale documents, forecast documents, retrieval notes, and harness-captured retrieval logs. Read the evaluation contract and output schemas. No CourtListener lookup, web search, corpus query, or open-events call was made by this evaluator; no new case facts were retrieved.

Reconstructed candidate-time statistical context using the contract-authorized statpack-only history helper:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000314/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000314/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000314/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All succeeded and resolved to build **886549a3ac32bdba039691b6d2ca7dc57bb72561**, landed October 13, 2026, digest **sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde**, with no alternative build. Inspected that historical Markdown table and corresponding baseline JSON rows to assess the candidates' statistical context. These commands emitted no `ranged corpus reads` line and retrieved no case-level corpus record. No predictor tree, identity map, or prediction history was consulted.
