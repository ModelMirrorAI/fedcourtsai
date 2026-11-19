Read the evaluation prompt and output schemas, the provisioned event and outcome, all three blinded candidates' predictions, rationales, forecast documents, retrieval notes and harness-captured logs, the case-level context and resolved docket snapshot, and relevant staged filings and document manifest. Consulted the committed statpack for context. No corpus query/open-events, CourtListener MCP lookup, web search, or external case-fact retrieval was performed by this evaluator. Candidate lookups quoted in the evaluations are evidence from their logs, not evaluator retrieval.

Reconstructed each candidate's historical statpack using the contract-authorized command:

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/73538544/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/73538544/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/73538544/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three commands succeeded and resolved prediction run 20261029T180303Z to build `7bcde3b105cb212283905eda17b827efc188e80c`, landed 2026-10-28T13:56:30-04:00, digest `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`; recorded digest and alternative SHA were null. Read the recovered sal-v4 tables and JSON to verify the candidates' historical base-rate usage. These commands read only statpack history; they are not corpus queries and emitted no `ranged corpus reads` line. No prediction history or alias mapping was consulted.
