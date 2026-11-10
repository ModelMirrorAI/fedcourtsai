# Evaluator retrieval

Read the evaluation contract, output schemas, resolved event and outcome, all three candidates' blinded predictions, rationale and forecast documents, their retrieval notes and harness-captured retrieval logs, and the case-level context, decided snapshot, document manifest, questions presented and relevant petition, opposition and appendix passages. No candidate identities were sought; no committed prediction tree, blinding machinery or topic-label artifacts were read.

Historical statpack verification used these commands, with synchronization disabled to avoid installing anything:

- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000249/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000249/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000249/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three reconstructed build 886549a3ac32bdba039691b6d2ca7dc57bb72561, landed October 13, 2026, digest sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde, with alternative_sha null. Read the reconstructed sal-v4 segment table and prior-Term baseline fields to assess the candidates' historical anchoring methods. No new baseline was computed for the evaluator's output.

No corpus query or open-events command, CourtListener lookup or web search was performed by the evaluator. The statpack commands printed no ranged-corpus-read lines. The candidate logs' described external lookups were reviewed only as staged evidence, not repeated.
