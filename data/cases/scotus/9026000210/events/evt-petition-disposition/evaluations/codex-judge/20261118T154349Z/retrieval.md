No corpus query, CourtListener MCP lookup, or web search was performed for this evaluation. Case facts were checked only against provisioned outcome, docket, briefs, and blinded candidate files; the opinion slots were absent. The committed statpack was consulted for context.

Historical base-rate context was reconstructed using these permitted local-history lookups:

- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9026000210/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All three succeeded and resolved the recorded cert-anchor digest to build `dedb32b153e67d254af10083c3ee247cecd56116` (landed October 31, 2026), digest `sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`, with no alternative build. Read the reconstructed statpack.md to assess historical table quotations. These commands emitted no `ranged corpus reads:` line; they read statpack history only, not the corpus or prediction history.
