# Retrieval record

No corpus query or open-events lookup, CourtListener MCP lookup, web search, external case-fact retrieval, or opinion retrieval was performed. Case assessment used the provisioned event, outcome, blinded candidate artifacts, questions presented, petition excerpts, appendix, context and docket snapshot. Output contracts and the committed metrics/statpack.md were read locally.

Historical base-rate verification used only the statpack history through the contract-authorized command, once per alias:

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000352/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000352/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000352/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three succeeded and recovered build `648fc43559f5480348a438523a81df100b5c7301` (landed `2026-10-30T20:13:49-04:00`), digest `sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`, recorded in each candidate's cert_anchor; alternative_sha was null. The recovered files have identical bytes. The historical markdown's relevant cert, marginal-cut and Term tables were read to assess the candidates' base-rate use. These local-history commands produce no ranged corpus reads line and were not corpus case lookups. No prediction history or identity mapping was read.

Local Python/jsonschema validation checks the required output files without running whole-tree validation.
