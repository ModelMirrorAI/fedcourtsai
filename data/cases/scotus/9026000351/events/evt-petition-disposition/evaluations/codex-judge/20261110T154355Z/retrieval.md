# Evaluator retrieval

Read the provisioned blinded candidates, their captured retrieval logs, the event and outcome, the case context, the November 9 snapshot, and the staged questions presented, petition excerpts, and appendix. Consulted the committed schemas and statpack for scoring context. No corpus query, CourtListener lookup, web search, external order retrieval, or new case-fact lookup was performed.

To evaluate each candidate's base-rate use against the build available at prediction time, ran:

1. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
2. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
3. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000351/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three succeeded and selected build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, landed October 19, 2026, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, with no alternative build. The candidate run identifier was read from its staged document. No candidate recorded a statpack digest. Read the recovered sal-v4 tables and JSON to verify strictly-prior-Term risk-set selection and distinguish the relist-zero grant and GVR categories. These commands access only statpack history, not prediction history, and emit no ranged-corpus-read line.

Historical statistics are context for rationale grading only. The harness supplies the stamped segment base rate and skill. Forecast claims are checked only against the staged case record; no missing order or writing was replaced with external material.
