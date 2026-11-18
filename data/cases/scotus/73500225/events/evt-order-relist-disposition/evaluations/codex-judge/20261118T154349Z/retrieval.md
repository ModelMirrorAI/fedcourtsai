No corpus queries, CourtListener MCP lookups, or web searches were performed.

Consulted the evaluation contract and schemas, the provisioned event and outcome, all three blinded candidates' prediction, reasoning, forecast and retrieval files, the terminal docket snapshot, document manifest, questions presented, and relevant petition/BIO/reply passages (including the lower-court opinion excerpt in the petition appendix). No external case facts or substitute opinion text were fetched.

Consulted the committed metrics/statpack.md and checked the committed pack digest. Because the candidates recorded an earlier build, ran:

`UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73500225/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

The command recovered build `ca0c9e1a49e292692bdc5b092cd9f868561169b8`, landed November 9, 2026 at 14:37:29 UTC, with recorded digest `sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653` and no alternative build. All three candidates carry that same recorded digest, so the recovered pack was used to check each one's historical references. Read its statpack.md and relevant statpack.json rows, confirming the frozen anchor and descriptive cuts. This command reads only statpack history and emits no ranged-corpus transfer line.
