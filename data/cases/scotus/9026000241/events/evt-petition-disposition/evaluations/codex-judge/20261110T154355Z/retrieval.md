# Evaluator retrieval

Read the evaluation contract and schemas, all three staged aliases' predictions, rationale and forecast documents, retrieval notes and harness-captured logs, the event and outcome, the final provisioned docket snapshot and context, and provisioned questions presented and relevant lower-court appendix text. No CourtListener MCP call, web search, corpus query or external order/opinion retrieval was made.

For the historical aggregate context used in the rationales, ran:

- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000241/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000241/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

Both returned build `a14b36a1e190a86d6a01df2ce410f5f9e54fb98b`, digest `sha256:84a5c25d4bf0a2a70ba5c6e9392e2e21d43ed5b794de0ae59c27cf1973ad0e7e`, no alternative build. These commands retrieve statpack history only, not candidate identities or prediction history. Consulted the reconstructed sal-v4 prior-Term reached-band table and terminal relist cuts. No ranged corpus reads line was emitted and no corpus rows were queried.

Local validation uses the existing Pydantic models after confirming their generated schemas exactly equal the checked-in evaluation and tooling JSON schemas; no packages were installed. Only this evaluator's contract-named output paths were written in the repository.
