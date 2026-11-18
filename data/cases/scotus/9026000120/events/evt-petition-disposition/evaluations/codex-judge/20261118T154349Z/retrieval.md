# Evaluator retrieval

Read the provisioned event, outcome, evaluator snapshot/context, cert filings, and all three blinded candidates' predictions, rationale/forecast documents, retrieval notes, and harness logs. Consulted the committed `metrics/statpack.md` for calibration context, then reconstructed the candidates' placement build to avoid treating later refreshes as errors.

No corpus query or open-events lookup, CourtListener MCP lookup, web search, or external opinion/order retrieval was performed by this evaluator. Candidates' described lookups are evidence being evaluated, not lookups performed in this run.

Historical statpack reconstruction commands:

- `UV_CACHE_DIR=/tmp/uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000120/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000120/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000120/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All succeeded and resolved to build `ca0c9e1a49e292692bdc5b092cd9f868561169b8` (landed November 9, 2026), digest `sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`, with no alternative build. These commands consult only statpack history and emit no ranged corpus reads line. Read the reconstructed markdown for calibration checks. Schema checks use local JSON schemas only.
