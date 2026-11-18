Read the provisioned event, outcome, blinded predictions/prose/logs, case context, completed docket, petition excerpts, questions presented, document manifest, and lower-court appendix. Consulted the committed metrics/statpack.md for source context; it is sal-v8 and differs from the candidates' sal-v4 build. No corpus query/open-events command, CourtListener MCP lookup, or web search was used by this evaluator.

Historical base-rate source checks, authorized by the evaluation contract:

- `UV_CACHE_DIR=/tmp/fedcourts-evaluate-uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
  - Succeeded. Prediction run: 20260927T182226Z; build: `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`; landed: 2026-09-26T08:09:47-04:00; digest: `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`; alternative_sha: null.
  - Read the reconstructed source pack to check the candidate's base-rate use. No ranged-corpus transfer line: statpack-at reads only statpack artifact history.
- `UV_CACHE_DIR=/tmp/fedcourts-evaluate-uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
  - Succeeded. Prediction run: 20260927T182226Z; build: `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`; landed: 2026-09-26T08:09:47-04:00; digest: `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`; alternative_sha: null.
  - Read the reconstructed source pack to check the candidate's base-rate use. No ranged-corpus transfer line: statpack-at reads only statpack artifact history.
- `UV_CACHE_DIR=/tmp/fedcourts-evaluate-uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - Succeeded. Prediction run: 20260927T182226Z; build: `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`; landed: 2026-09-26T08:09:47-04:00; digest: `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`; alternative_sha: null.
  - Read the reconstructed source pack to check the candidate's base-rate use. No ranged-corpus transfer line: statpack-at reads only statpack artifact history.

These checks preserve the blind and retrieve no new case facts. No substitute opinion, disposing order, or commentary was fetched.
