# Evaluator retrieval

Read only the provisioned blinded candidate files, event and outcome, staged case context, docket snapshot, petition question, opposition excerpt and lower-court appendix excerpt; also read the evaluation/tooling/flags schemas, evaluation contract, and committed statpack context. No corpus query or open-events lookup, CourtListener MCP lookup, web search, external case retrieval, or substitute opinion retrieval was performed.

To avoid judging historical base-rate use against a refreshed pack, reconstructed only statpack history with these commands:

- `UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000249/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000249/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000249/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All three initial attempts failed before retrieval because the default uv cache was read-only. Reissued each command with `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`; all succeeded without installing packages. Each resolved to build `061c238147aa000fa108f3b389e44f43cca52e87`, landed `2026-08-25T13:24:29-04:00`, digest `sha256:0d05c670da5896c5e3078e0f81cbb775a2045fc05432d8d957b929849c02f891`, with no alternative build. Read the historical table to assess method, not to create a scored baseline. These local-history commands emit no ranged-corpus-read line and do not retrieve case facts.
