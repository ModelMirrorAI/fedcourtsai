# Evaluator retrieval record

Read the evaluation prompt and schemas; the provisioned event, outcome, case context, snapshot, document manifest, question presented, and relevant portions of the petition and supplemental brief; and every candidate's blinded prediction, rationale, forecast, retrieval note, and harness-captured retrieval log. No candidate identities or committed prediction trees were consulted. No corpus query, CourtListener lookup, web search, external opinion, or external order was used.

For candidate-era base-rate provenance, attempted the following commands, each initially failing because the default uv cache was read-only:

- `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000462/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000462/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000462/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

Retried all three successfully with `UV_CACHE_DIR=/tmp/uv-cache` preceding each command. These commands consult only statpack history, not prediction history or case membership. Each returned build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, landed `2026-09-28T08:12:04-04:00`, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, and `alternative_sha: null`. I read the reconstructed `sal-v4` table and inspected its JSON structure to assess the candidates' historical population choices, without producing an independent scored anchor. These are local statpack-history reads and print no ranged-corpus-read transfer line.
