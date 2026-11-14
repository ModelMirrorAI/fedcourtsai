# Evaluator retrieval

Read the evaluation contract and output schemas, the event and outcome, all three blinded candidates' predictions, rationales, forecast documents, retrieval notes and harness logs, and the provisioned case snapshot and relevant filing passages. Checked that no opinion slot was staged. Consulted the committed statpack for context, not as a replacement for the candidates' historical build.

Reconstructed only statpack history, without reading prediction history or identity mappings:

- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 UV_OFFLINE=1 uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All three returned build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, landed `2026-10-19T08:07:55-04:00`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, and no alternative build. The commands emit no ranged-corpus transfer line. Scratch artifacts were inspected only to assess historical base-rate use.

No corpus queries, CourtListener MCP lookups, web searches, or external order/opinion retrievals were performed by the evaluator. Candidate retrievals described in their logs are not evaluator retrievals.
