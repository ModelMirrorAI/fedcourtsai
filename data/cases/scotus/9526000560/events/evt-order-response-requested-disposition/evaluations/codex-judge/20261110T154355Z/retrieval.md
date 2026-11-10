# Evaluator retrieval record

Read the evaluation contract and output schemas; this event's definition and outcome; all three candidates' blinded predictions, rationale and forecast documents, retrieval notes, and harness-captured retrieval logs; the case's provisioned context, decided docket snapshot, application excerpts, and staged per-curiam writing and writings manifest. Read the committed statpack's interim section for baseline availability and historical-use context. No corpus query, open-events lookup, CourtListener MCP lookup, web search, or external case-fact retrieval was performed by this evaluator. Candidate lookup descriptions are evidence of their activity, not lookups performed by this evaluator.

Historical statpack reconstruction, confined to statpack history:

1. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9526000560/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
2. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9526000560/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
3. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts statpack-at data/cases/scotus/9526000560/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three succeeded and resolved prediction run `20261023T210522Z` to build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, landed `2026-10-19T08:07:55-04:00`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, with no alternative build. Read the reconstructed interim table for codex-baseline; the three reconstructed builds are identical. These local history commands emitted no `ranged corpus reads` line and were not corpus lookups.

No candidate-identification route, prediction history, alias map, or labeling-measurement artifact was consulted. JSON schema and model validation and alias/output-scope checks are local validation, not substantive retrieval.
