# Evaluator retrieval

- Read the evaluation contract and schemas; the provisioned event, outcome, context, resolved docket snapshot, document manifest, questions presented, and relevant portions of the SG invited brief, opposition, and cert reply; and every staged candidate's prediction, rationale, forecast, retrieval note, and full logged call list. No candidate identity lookup, prediction-tree read, corpus query, CourtListener lookup, web search, external order, or external opinion retrieval was performed.
- Reconstructed the statistical context available to each candidate using the contract's historical-statpack helper:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73278467/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73278467/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73278467/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- All three helpers succeeded with build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, landed October 19, 2026; digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`; no recorded candidate digest and no alternative build. Inspected that reconstructed build's CVSG, relist, and sal-v4 band tables to audit the candidates' stated context, not to supply an evaluator scoring baseline.
- These historical-statpack reads produced no `ranged corpus reads` line and did not query the corpus. No packages were installed.
