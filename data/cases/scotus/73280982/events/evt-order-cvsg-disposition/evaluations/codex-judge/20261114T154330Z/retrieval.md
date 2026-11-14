# Evaluator retrieval

Read the evaluation contract, output schemas, this event's definition and outcome, all three blinded candidates' predictions, rationale and forecast documents, retrieval notes and captured retrieval logs, the evaluator context, the November 14 snapshot, and relevant staged document passages. The staged SG brief and November 13 docket order supplied the evidence for question selection and procedural route. No opinion body was staged and none was fetched.

Historical base-rate context was checked with the following local, statpack-history-only commands. `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache` was set to use existing tooling without package installation:

- `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

All three returned build `73762050f49cd68912e89c864e25a792e498b45a`, landed `2026-09-14T08:42:59-04:00`, digest `sha256:345aff2a4fcdad755e6606d092e6c2475966c0bd858d291155914ef722d88fe8`, no recorded candidate digest and no alternative SHA. Read the recovered high-band prior-Term rows and CVSG table, and the current statpack's opening context. These were checks of candidates' historical analysis, not an independently supplied scored baseline. These commands report no ranged-corpus transfer line.

No corpus query or open-events call, CourtListener MCP lookup, web search, external order, or commentary was consulted by this evaluator. Candidates' historical retrievals are evidence about the candidates, not lookups performed by this cell. Local schema/model validation is the only remaining tooling beyond these record reads.
