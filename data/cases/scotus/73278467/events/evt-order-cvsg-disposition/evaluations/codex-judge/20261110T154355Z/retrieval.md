# Evaluator retrieval

No external case-fact retrieval, CourtListener MCP lookup, web search, or corpus `query`/`open-events` call was made. Grading used the provisioned event, outcome, blinded candidates and captured logs, docket snapshot, questions presented, and staged petition/opposition/SG materials. No opinion slot was staged; no substitute opinion was fetched.

Repository reference material: evaluation and feedback schemas, the evaluation contract, and the committed statpack's scope header. Prediction-time statistical artifacts were reconstructed using only the statpack's permitted history:

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73278467/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73278467/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73278467/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All succeeded and selected build `73762050f49cd68912e89c864e25a792e498b45a`, landed September 14, 2026, digest `sha256:345aff2a4fcdad755e6606d092e6c2475966c0bd858d291155914ef722d88fe8`, with no recorded candidate digest and no alternative build. Inspected the reconstructed CVSG table and strictly-prior-Term high-band reached fields to assess the candidates' statistical methodology. These are local historical-artifact lookups, not corpus queries; they emit no `ranged corpus reads` line. No evaluator-scored baseline was substituted for the harness stamp.
