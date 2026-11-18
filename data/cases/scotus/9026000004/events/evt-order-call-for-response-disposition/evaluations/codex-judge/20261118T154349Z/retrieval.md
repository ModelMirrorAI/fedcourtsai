# Evaluator retrieval record

Read the evaluation prompt, output schemas, resolved event and outcome, all three blinded candidates' prediction/rationale/forecast/retrieval files and harness logs, the provisioned context and November 16 snapshot, and the staged questions presented, petition and appellate appendix, document manifest, and brief in opposition. No majority opinion or writings were staged; no replacement was fetched.

Consulted the committed `metrics/statpack.md` to identify its current salience version. Reconstructed each candidate's historical statistical inputs with these commands:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000004/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All succeeded and selected the same `sal-v4` build: `7bcde3b105cb212283905eda17b827efc188e80c`, landed October 28, 2026; digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, with `alternative_sha: null`. Read the reconstructed Markdown's population cuts and per-Term risk-set table and its JSON to verify the candidates' statistical descriptions. These commands consult statpack history only; none printed a `ranged corpus reads` line.

No evaluator corpus query, CourtListener MCP lookup, or web search was performed. Candidate lookups described in their staged logs were reviewed as evidence and were not repeated. Only the authorized evaluator output files were written in the repository; reconstructed statpacks remained in the contract-authorized scratch paths.
