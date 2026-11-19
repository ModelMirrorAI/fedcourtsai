# Evaluator retrieval

Read the evaluation contract, output schemas, event and outcome, all three blinded candidates' prediction, rationale, forecast and retrieval files, the staged context and decided docket snapshot, and the staged questions presented, document manifest, relevant petition and appellate-appendix excerpts, and brief in opposition. No majority-opinion or other writing slot was staged. Consulted the committed metrics/statpack.md for base-rate context.

Reconstructed each candidate's contemporary statpack using:

- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/73272491/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All three succeeded and selected build `7bcde3b105cb212283905eda17b827efc188e80c` (landed 2026-10-28T13:56:30-04:00), digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, with no alternative build. Read the reconstructed markdown to assess the candidates' historical table use. These commands consult statpack history only; no corpus-transfer line was emitted.

No corpus query/open-events, CourtListener MCP lookup, or web retrieval was performed by this evaluator. Candidate retrievals discussed in the evaluations are evidence read from the blinded inputs, not additional evaluator lookups.
