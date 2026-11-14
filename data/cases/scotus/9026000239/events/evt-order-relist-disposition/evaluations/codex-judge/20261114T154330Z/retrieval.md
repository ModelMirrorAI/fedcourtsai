# Evaluator retrieval

Read the evaluation contract, output schemas, this event's event.yaml and outcome.json, the case-level context, resolved November 13 snapshot, provisioned filing excerpts and manifest, and all three blinded candidates' prediction, rationale, forecast, retrieval note, and harness-captured retrieval log. Read the committed statpack as reference context.

Reconstructed the prediction-time reference pack using these commands, each prefixed with `UV_CACHE_DIR=/tmp/uv-cache`:

- `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000239/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

Each recovered build `ca0c9e1a49e292692bdc5b092cd9f868561169b8`, digest `sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`, landed November 9, 2026 at 14:37:29 UTC, with alternative_sha null. These are local statpack-history reconstructions, not corpus queries; no `ranged corpus reads` line was emitted. Consulted the recovered salience-band and relist tables to evaluate the candidates against the pack they actually used, without computing a replacement evaluation baseline.

No evaluator corpus query/open-events call, CourtListener MCP lookup, or web search was made. Candidate retrieval described in their evaluations is evidence from the staged logs, not fresh evaluator retrieval. No packages were installed. JSON schema checks use the existing system Python jsonschema installation.
