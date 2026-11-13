# Evaluation retrieval

No corpus query, CourtListener lookup, or web retrieval was performed by this evaluator. Case facts and forecast grades use only the staged candidates, committed outcome, application, and provisioned November 12 docket snapshot. The opinion slot contains no staged opinion or separate-writing files.

For statistical context I read the committed interim section of `metrics/statpack.md` and `metrics/statpack.json`. To avoid grading a candidate against a later build, I ran:

`UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9526000661/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

It reconstructed build `ca0c9e1a49e292692bdc5b092cd9f868561169b8`, landed November 9, 2026 at 14:37:29 UTC, with recorded and reconstructed digest `sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`; no alternative build was reported. Each of gemini-baseline, codex-baseline, and claude-baseline records that identical digest, so the reconstructed bytes were used for all three base-rate-use checks. This command consults statpack history only and prints no `ranged corpus reads` transfer line. I inspected its interim counts and applicant-class table, not case history or predictor identity material.
