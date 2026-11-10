# Evaluator retrieval

No external retrieval of case facts, opinions, orders, or commentary. I read the provisioned outcome, event, context, snapshot, staged per curiam and writings manifest, and each blinded candidate's prediction, rationale, forecast, retrieval note, and captured retrieval log. I also consulted the committed schemas and interim statpack section.

Historical statpack reconstruction only, within the blind:

- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9526000560/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9526000560/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9526000560/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All three succeeded and selected build eb6830084a187953fd58b91cb3c9125fc6775a7b, landed October 19, 2026, with digest sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba, no recorded candidate digest, and no alternative build. This command reads statpack history only, not candidate identities or prediction history. It emits no ranged-corpus-transfer line. Historical tables were used to check each rationale's base-rate reporting, not to assign the harness's scored baseline.

No `fedcourts query` or `open-events` call, CourtListener MCP lookup, or evaluator web search was performed. Tool calls described inside candidate logs were reviewed as evidence and were not reissued.
