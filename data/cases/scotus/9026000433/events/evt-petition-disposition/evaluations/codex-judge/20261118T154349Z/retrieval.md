No corpus queries, CourtListener MCP calls, or web searches were made by this evaluator. Case evidence was limited to the provisioned event, outcome, blinded candidate documents/logs, snapshot and extracted filings.

The current committed metrics/statpack.md was consulted for context. The prediction-time pack was reconstructed separately for each alias using the authorized statpack-history helper:

- Initial attempt: `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000433/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` failed before execution because the default uv cache was read-only.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000433/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000433/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000433/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All three succeeded at build 7bcde3b105cb212283905eda17b827efc188e80c, landed 2026-10-28T13:56:30-04:00, digest sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641; no alternative build. These history-only calls printed no ranged-corpus-reads line. The reconstructed claude-baseline statpack.md and prior-Term segment fields in statpack.json were inspected; the other aliases resolved to the same build. No case or prediction history was inspected.

Local tools read the evaluation contract and schemas, listed filenames, inspected git status, wrote the authorized outputs, and validated JSON against the supplied schemas. No packages were installed.
