# Evaluator retrieval

Reviewed only this cell's event/outcome, case-level provisioned docket, questions presented and petition excerpts, blinded candidate documents and captured retrieval logs, plus the evaluation contract and schemas. No corpus query, CourtListener lookup, external web search or new case-fact retrieval was performed.

To check candidate base-rate provenance without consulting prediction history, ran:

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000018/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000018/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000018/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All resolved to build 7bcde3b105cb212283905eda17b827efc188e80c, landed October 28, 2026, digest sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641, with no alternative build. Read the reconstructed sal-v4 state risk-set rows to verify historical use. These are local statpack-history lookups, not ranged corpus reads; no transfer line was emitted. No evaluator baseline was independently pooled or quoted.
