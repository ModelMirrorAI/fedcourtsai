# Evaluator retrieval record

Read the evaluation contract and schemas, the event definition and outcome, the provisioned context, November 9 snapshot, questions presented, document manifest and relevant petition/appendix passages, and all three blinded candidates' prediction, rationale, forecast, retrieval note and complete retrieval-log call lists. Candidate log queries were treated as evidence, not executed.

To audit historical base-rate use without substituting the evaluator's newer context, ran these permitted statpack-history lookups:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000115/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000115/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000115/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

Each returned build 886549a3ac32bdba039691b6d2ca7dc57bb72561, landed October 13, 2026, digest sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde, with no alternative build. Read the recovered sal-v4 segment table and JSON field structure. These commands read statpack history only, not prediction history, and reported no ranged-corpus-read transfer line. No evaluation baseline was independently pooled.

No evaluator corpus query, open-events lookup, CourtListener MCP lookup, web search or external legal-source retrieval was performed. No opinion or order was fetched to supplement the staged record. Local schema validation uses the preinstalled system Python jsonschema package and the repository's Evaluation and AgentToolingFeedback models; nothing was installed.
